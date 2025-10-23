from django.conf import settings
from rest_framework import generics, status
from rest_framework.decorators import api_view, throttle_classes, parser_classes
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from django.utils.timezone import now, localtime
from django.db.models import Count, Max
import csv, io, re
from django.core.validators import EmailValidator
from django.core.mail import EmailMultiAlternatives, get_connection
from rest_framework.parsers import MultiPartParser, FormParser

from .utils import (
    generate_token,
    render_token_email_html,
    render_token_email_text,
)

from datetime import date

from .models import Election, Candidate, Vote, VoterToken, FraudReport
from .serializers import (
    ElectionSerializer, CandidateSerializer, ResultSerializer, VoteSerializer,
    FraudReportSerializer, ElectionAdminUpdateSerializer, CandidateAdminCreateSerializer
)

def require_admin(request):
    key = request.headers.get('X-Admin-Key')
    if not key or key != getattr(settings, "ADMIN_API_KEY", ""):
        return False
    return True

email_validator = EmailValidator()
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")

def _normalize_email(s: str) -> str:
    return (s or '').strip().lower()

def get_active_election():
    today = date.today()
    return Election.objects.filter(start_date__lte=today, end_date__gte=today).order_by('-year').first()

class ActiveElectionView(generics.RetrieveAPIView):
    serializer_class = ElectionSerializer
    def get_object(self):
        obj = get_active_election()
        if obj is None:
            raise generics.exceptions.NotFound("Tidak ada election aktif.")
        return obj

class CandidateList(generics.ListAPIView):
    serializer_class = CandidateSerializer
    def get_queryset(self):
        election_id = self.request.query_params.get('election')
        if election_id:
            return Candidate.objects.filter(election_id=election_id)
        active = get_active_election()
        return Candidate.objects.filter(election=active) if active else Candidate.objects.none()

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def admin_import_voters(request):
    if not require_admin(request):
        return Response({"detail": "Unauthorized"}, status=401)

    election_id = request.POST.get('election_id')
    overwrite_flag = request.POST.get('overwrite', 'false').lower() == 'true'

    if not election_id:
        return Response({"detail": "election_id wajib"}, status=400)

    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        return Response({"detail": "Election tidak ditemukan."}, status=404)

    file = request.FILES.get('file')
    if not file:
        return Response({"detail": "file CSV tidak ditemukan (field name: file)."}, status=400)

    try:
        raw = file.read().decode('utf-8-sig')
    except Exception:
        return Response({"detail": "Gagal membaca CSV. Pastikan encoding UTF-8."}, status=400)

    f = io.StringIO(raw)
    try:
        sample = raw[:1024]
        has_header = csv.Sniffer().has_header(sample) if sample else False
    except Exception:
        has_header = False

    reader = csv.DictReader(f) if has_header else csv.DictReader(f, fieldnames=['email'])

    created, updated, skipped_invalid, skipped_duplicate = 0, 0, 0, 0
    seen_in_file = set()  # hindari duplikat di file yang sama

    for row in reader:
        email = _normalize_email(row.get('email'))
        if not email or email in seen_in_file:
            skipped_duplicate += 1 if email else 0
            continue
        seen_in_file.add(email)

        if not EMAIL_RE.match(email):
            skipped_invalid += 1
            continue
        try:
            email_validator(email)
        except Exception:
            skipped_invalid += 1
            continue

        vt_qs = VoterToken.objects.filter(email=email, election=election)
        if vt_qs.exists():
            if overwrite_flag:
                vt = vt_qs.first()
                vt.token = generate_token()
                vt.used = False
                vt.emailed_at = None  # reset status kirim, karena token baru
                vt.save(update_fields=['token', 'used', 'emailed_at'])
                updated += 1
            else:
                skipped_duplicate += 1
        else:
            VoterToken.objects.create(email=email, token=generate_token(), election=election)
            created += 1

    return Response({
        "election": election.id,
        "created": created,
        "updated": updated,
        "skipped_invalid": skipped_invalid,
        "skipped_duplicate": skipped_duplicate,
    }, status=200)

@api_view(['POST'])
def admin_send_tokens(request):
    if not require_admin(request):
        return Response({"detail": "Unauthorized"}, status=401)

    election_id = request.data.get('election_id') or request.POST.get('election_id')
    resend_all = str(request.data.get('resend_all') or request.POST.get('resend_all') or 'false').lower() == 'true'

    if not election_id:
        return Response({"detail": "election_id wajib"}, status=400)

    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        return Response({"detail": "Election tidak ditemukan."}, status=404)

    qs = VoterToken.objects.filter(election=election)
    if not resend_all:
        qs = qs.filter(emailed_at__isnull=True)

    total_candidates = qs.count()
    if total_candidates == 0:
        return Response({"detail": "Tidak ada token yang perlu dikirim."}, status=200)

    messages = []
    election_name = f"Election {election.year} PPI Osaka–Nara"
    subject = f"Token Voting PPI Osaka–Nara {election.year}"
    vote_link = settings.FRONTEND_VOTE_URL
    vote_deadline = election.end_date.strftime('%Y-%m-%d')
    support_email = settings.SUPPORT_EMAIL

    # Kirim satu per satu agar bisa tandai keberhasilan per email
    sent = 0
    errors = 0
    failed_list = []

    with get_connection() as conn:
        for vt in qs.iterator():
            text_body = render_token_email_text(
                election_name=election_name,
                token=vt.token,
                vote_link=vote_link,
                vote_deadline=vote_deadline,
                email=vt.email,
                election_year=election.year,
                support_email=support_email,
            )
            html_body = render_token_email_html(
                election_name=election_name,
                token=vt.token,
                vote_link=vote_link,
                vote_deadline=vote_deadline,
                email=vt.email,
                election_year=election.year,
                support_email=support_email,
            )
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[vt.email],
                headers={'Reply-To': support_email},
            )
            msg.attach_alternative(html_body, "text/html")
            try:
                num = conn.send_messages([msg])
                if num == 1:
                    vt.emailed_at = now()
                    vt.save(update_fields=['emailed_at'])
                    sent += 1
                else:
                    errors += 1
                    failed_list.append(vt.email)
            except Exception:
                errors += 1
                failed_list.append(vt.email)

    return Response({
        "election": election.id,
        "attempted": total_candidates,
        "sent": sent,
        "failed": errors,
        "failed_list": failed_list[:50],  # batasi agar respons tidak terlalu besar
        "resend_all": resend_all,
    }, status=200)

@api_view(['GET'])
def admin_voter_stats(request):
    if not require_admin(request):
        return Response({"detail": "Unauthorized"}, status=401)

    election_id = request.query_params.get('election_id')
    if not election_id:
        return Response({"detail": "election_id wajib"}, status=400)

    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        return Response({"detail": "Election tidak ditemukan."}, status=404)

    qs = VoterToken.objects.filter(election=election)
    total = qs.count()
    pending = qs.filter(emailed_at__isnull=True).count()
    sent = total - pending
    used = qs.filter(used=True).count()
    last_sent = qs.aggregate(last=Max('emailed_at'))['last']

    return Response({
        "election": election.id,
        "total": total,
        "pending": pending,
        "sent": sent,
        "used": used,
        "last_sent_at": last_sent,
    }, status=200)

@api_view(['POST'])
@throttle_classes([ScopedRateThrottle])
def token_login(request):
    request.throttle_scope = 'token_login'
    email = request.data.get('email', '').strip().lower()
    token = request.data.get('token', '').strip()
    active = get_active_election()
    
    if not active:
        return Response({"code":"NO_ELECTION","detail":"Tidak ada election aktif."}, status=400)

    try:
        vt = VoterToken.objects.get(email=email, token=token, election=active)
    except VoterToken.DoesNotExist:
        return Response({"code":"INVALID_CREDENTIALS","detail":"Email/token tidak valid."}, status=400)

    # CEK SUDAH VOTE? (Check this BEFORE checking is_open)
    voted = Vote.objects.filter(election=active, email=email).select_related('candidate').first()
    if vt.used or voted:
        return Response({
            "code":"ALREADY_VOTED",
            "detail":"Anda sudah melakukan voting.",
            "election_id": active.id,
            "voted_for": voted.candidate.name if voted else None,
            "candidate_id": voted.candidate_id if voted else None
        }, status=400)

    # Check if voting is still open AFTER checking if already voted
    if not active.is_open:
        return Response({"code":"ELECTION_CLOSED","detail":"Voting sudah ditutup."}, status=400)

    # token untuk sesi (dummy)
    return Response({"access": f"DUMMY-{email}", "election_id": active.id})

@api_view(['POST'])
@throttle_classes([ScopedRateThrottle])
def cast_vote(request):
    request.throttle_scope = 'cast_vote'
    email = request.data.get('email', '').strip().lower()
    token = request.data.get('token', '').strip()
    candidate_id = request.data.get('candidate_id')

    active = get_active_election()
    if not active or not active.is_open:
        return Response({"code":"ELECTION_CLOSED","detail":"Voting belum dibuka."}, status=400)

    try:
        vt = VoterToken.objects.get(email=email, token=token, election=active)
    except VoterToken.DoesNotExist:
        return Response({"code":"INVALID_CREDENTIALS","detail":"Email/token tidak valid."}, status=400)

    if vt.used or Vote.objects.filter(election=active, email=email).exists():
        return Response({"code":"ALREADY_VOTED","detail":"Anda sudah melakukan voting."}, status=400)

    try:
        cand = Candidate.objects.get(id=candidate_id, election=active)
    except Candidate.DoesNotExist:
        return Response({"code":"CANDIDATE_NOT_FOUND","detail":"Kandidat tidak ditemukan."}, status=404)

    Vote.objects.create(election=active, candidate=cand, email=email)
    vt.used = True
    vt.save(update_fields=['used'])
    return Response({"ok": True, "detail": "Vote tercatat."}, status=201)

@api_view(['GET'])
def results_view(request):
    election_id = request.query_params.get('election')
    try:
        election = Election.objects.get(id=election_id)
    except Election.DoesNotExist:
        return Response({"detail": "Election tidak ditemukan."}, status=404)
    if not election.show_results:
        return Response([], status=200)

    qs = Vote.objects.filter(election=election).values('candidate_id', 'candidate__name').annotate(votes=Count('id'))
    data = [{
        "candidate_id": r['candidate_id'],
        "candidate_name": r['candidate__name'],
        "votes": r['votes']
    } for r in qs]
    ser = ResultSerializer(data=data, many=True)
    ser.is_valid(raise_exception=True)
    return Response(ser.data)

@api_view(['GET'])
def debug_date(request):
    return Response({
        "now_date": now().date(),
        "localtime_date": localtime(now()).date(),
        "system_date": date.today(),
        "timezone": settings.TIME_ZONE,
    })

@api_view(['POST'])
def token_login(request):
    email = request.data.get('email', '').strip().lower()
    token = request.data.get('token', '').strip()
    active = get_active_election()
    if not active or not active.is_open:
        return Response({"detail": "Voting belum dibuka."}, status=400)

    try:
        vt = VoterToken.objects.get(email=email, token=token, election=active)
    except VoterToken.DoesNotExist:
        return Response({"detail": "Email/token tidak valid."}, status=400)

    # “Access” dummy (supaya frontend bisa lanjut). Produksi nanti pakai JWT.
    return Response({"access": f"DUMMY-{email}"})

@api_view(['POST'])
def cast_vote(request):
    email = request.data.get('email', '').strip().lower()
    token = request.data.get('token', '').strip()
    candidate_id = request.data.get('candidate_id')

    active = get_active_election()
    if not active or not active.is_open:
        return Response({"detail": "Voting belum dibuka."}, status=400)

    try:
        vt = VoterToken.objects.get(email=email, token=token, election=active)
    except VoterToken.DoesNotExist:
        return Response({"detail": "Email/token tidak valid."}, status=400)

    if vt.used:
        return Response({"detail": "Anda sudah melakukan voting."}, status=400)

    try:
        cand = Candidate.objects.get(id=candidate_id, election=active)
    except Candidate.DoesNotExist:
        return Response({"detail": "Kandidat tidak ditemukan."}, status=404)

    # Cegah double vote per email
    if Vote.objects.filter(election=active, email=email).exists():
        return Response({"detail": "Anda sudah melakukan voting."}, status=400)

    Vote.objects.create(election=active, candidate=cand, email=email)
    vt.used = True
    vt.save(update_fields=['used'])
    return Response({"detail": "Vote tercatat."}, status=201)

class FraudReportCreate(generics.CreateAPIView):
    serializer_class = FraudReportSerializer
    queryset = FraudReport.objects.all()

    @throttle_classes([ScopedRateThrottle])
    def post(self, request, *args, **kwargs):
        request.throttle_scope = 'reports'
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        obj = serializer.save()
        try:
            send_mail(
                subject=f"[KPU] Laporan kecurangan dari {obj.name}",
                message=(
                    f"Nama   : {obj.name}\n"
                    f"Email  : {obj.email}\n"
                    f"Waktu  : {obj.created_at}\n\n"
                    f"Pesan:\n{obj.message}"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SUPPORT_EMAIL],
                fail_silently=True,  # prod: True; dev: bisa False untuk debug
            )
        except Exception:
            pass

# ========== ADMIN ENDPOINTS ==========
@api_view(['GET', 'POST'])
def admin_elections(request):
    if not require_admin(request):
        return Response({"detail": "Unauthorized"}, status=401)

    if request.method == 'GET':
        qs = Election.objects.all().order_by('-year')
        return Response(ElectionSerializer(qs, many=True).data)

    # POST: create election baru (default is_open False, show_results False)
    data = request.data.copy()
    data.setdefault('is_open', False)
    data.setdefault('show_results', False)
    ser = ElectionAdminUpdateSerializer(data=data)
    ser.is_valid(raise_exception=True)
    election = Election.objects.create(**ser.validated_data)
    return Response(ElectionSerializer(election).data, status=201)

@api_view(['GET', 'PUT'])
def admin_active_election(request):
    if not require_admin(request):
        return Response({"detail": "Unauthorized"}, status=401)

    active = get_active_election()
    
    if request.method == 'GET':
        if not active:
            return Response({
                "detail": "Tidak ada election aktif.",
                "id": None,
                "year": None,
                "start_date": None,
                "end_date": None,
                "is_open": False,
                "show_results": False
            }, status=200)
        return Response(ElectionSerializer(active).data)

    # PUT: update existing election or create if ?id= provided
    election_id = request.query_params.get('id')
    
    if election_id:
        # Update specific election by ID
        try:
            election = Election.objects.get(pk=election_id)
        except Election.DoesNotExist:
            return Response({"detail": "Election tidak ditemukan."}, status=404)
        
        ser = ElectionAdminUpdateSerializer(election, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        election = ser.save()
        return Response(ElectionSerializer(election).data)
    
    # Update active election or create new one if no active election exists
    if not active:
        # No active election, create new one
        ser = ElectionAdminUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        election = Election.objects.create(**ser.validated_data)
        return Response(ElectionSerializer(election).data, status=201)
    
    # Update existing active election
    ser = ElectionAdminUpdateSerializer(active, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    election = ser.save()
    return Response(ElectionSerializer(election).data)

@api_view(['POST'])
def admin_candidate_create(request):
    if not require_admin(request):
        return Response({"detail": "Unauthorized"}, status=401)

    ser = CandidateAdminCreateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    cand = ser.save()
    return Response(CandidateSerializer(cand).data, status=201)

@api_view(['PATCH', 'DELETE'])
def admin_candidate_detail(request, pk):
    if not require_admin(request):
        return Response({"detail": "Unauthorized"}, status=401)
    try:
        cand = Candidate.objects.get(pk=pk)
    except Candidate.DoesNotExist:
        return Response({"detail": "Kandidat tidak ditemukan."}, status=404)

    if request.method == 'PATCH':
        ser = CandidateAdminCreateSerializer(cand, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        cand = ser.save()
        return Response(CandidateSerializer(cand).data)

    # DELETE
    cand.delete()
    return Response(status=204)
