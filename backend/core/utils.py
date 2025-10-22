import secrets
import string

def generate_token(length=6):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

EMAIL_TEMPLATE_HTML = """<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Token Pemungutan Suara – KPU PPI Osaka–Nara</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
  </head>
  <body style="margin:0;background:#f6f7fb;font-family:-apple-system,Roboto,'Helvetica Neue',Arial;line-height:1.6;color:#111;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center" style="padding:24px;">
          <table role="presentation" width="640" cellpadding="0" cellspacing="0" style="background:#fff;border:1px solid #e7e7ef;border-radius:10px;overflow:hidden;">
            <tr>
              <td style="padding:20px 24px;background:#102a43;color:#fff;">
                <div style="font-size:14px;opacity:.9;letter-spacing:.4px;">Komisi Pemilihan Umum</div>
                <div style="font-size:18px;font-weight:700;margin-top:4px;">PPI Osaka–Nara</div>
                <div style="font-size:12px;opacity:.9;margin-top:4px;">{election_name}</div>
              </td>
            </tr>
            <tr>
              <td style="padding:24px;">
                <p style="margin:0 0 10px 0;">Yth. Pemilih,</p>
                <p style="margin:0 0 16px 0;">
                  Anda menerima email ini karena terdaftar sebagai pemilih pada pemilihan <strong>{election_name}</strong>.
                  Token pemungutan suara Anda tercantum di bawah ini. Simpan dan gunakan hanya pada laman resmi voting.
                </p>
                <div style="margin:16px 0;padding:16px;border:1px dashed #c7c9d9;background:#fafbff;border-radius:8px;text-align:center;">
                  <div style="font-size:12px;color:#666;margin-bottom:6px;">TOKEN PEMILIH</div>
                  <div style="font-size:22px;font-weight:800;letter-spacing:1px;">{token}</div>
                </div>
                <div style="margin:18px 0 8px 0;">
                  <a href="{vote_link}" style="display:inline-block;padding:12px 18px;background:#2260ff;color:#fff;text-decoration:none;border-radius:8px;font-weight:700;">
                    Buka Laman Voting
                  </a>
                </div>
                <div style="font-size:12px;color:#666;margin:4px 0 16px 0;">
                  Jika tombol tidak berfungsi, salin tautan ini ke peramban Anda: <br>
                  <span style="word-break:break-all;color:#2260ff;">{vote_link}</span>
                </div>
                <p style="margin:0 0 16px 0;">
                  <strong>Batas waktu pemungutan suara:</strong> {vote_deadline}
                </p>
                <div style="margin:12px 0 0 0;padding:12px 14px;background:#fff8e6;border:1px solid #ffe3a3;border-radius:8px;">
                  <div style="font-weight:700;margin-bottom:6px;">Penting:</div>
                  <ul style="margin:0 0 0 18px;padding:0;">
                    <li>Token bersifat <strong>unik</strong> dan <strong>rahasia</strong> untuk satu pemilih satu suara.</li>
                    <li>Jangan membagikan token ini kepada siapa pun, termasuk panitia.</li>
                    <li>Email terdaftar: <strong>{email}</strong>.</li>
                  </ul>
                </div>
                <p style="margin:16px 0 0 0;font-size:14px;">
                  Jika Anda merasa tidak seharusnya menerima email ini, abaikan email ini dan hubungi panitia di
                  <a href="mailto:{support_email}" style="color:#2260ff;text-decoration:none;">{support_email}</a>.
                </p>
              </td>
            </tr>
            <tr>
              <td style="padding:16px 24px;background:#f2f4f8;color:#556070;font-size:12px;">
                <div style="margin-bottom:4px;">&copy; {election_year} Komisi Pemilihan Umum – PPI Osaka–Nara</div>
                <div style="opacity:.9;">
                  Surat ini dikirim otomatis. Mohon tidak membalas ke alamat ini. Untuk bantuan, gunakan alamat kontak panitia di atas.
                </div>
              </td>
            </tr>
          </table>
          <div style="font-size:11px;color:#8a8fa3;margin-top:10px;">
            Dokumen resmi KPU PPI Osaka–Nara.
          </div>
        </td>
      </tr>
    </table>
  </body>
</html>
"""

def render_token_email_html(*, election_name, token, vote_link, vote_deadline, email, election_year, support_email):
    html = EMAIL_TEMPLATE_HTML.format(
        election_name=election_name,
        token=token,
        vote_link=vote_link,
        vote_deadline=vote_deadline,
        email=email,
        election_year=election_year,
        support_email=support_email or settings.SUPPORT_EMAIL,
    )
    return html

def render_token_email_text(*, election_name, token, vote_link, vote_deadline, email, election_year, support_email):
    # Versi teks polos sebagai fallback
    text = (
        f"Komisi Pemilihan Umum – PPI Osaka–Nara\n"
        f"{election_name}\n\n"
        f"Yth. Pemilih,\n"
        f"Anda terdaftar sebagai pemilih pada {election_name}.\n"
        f"Token pemungutan suara Anda:\n"
        f"  {token}\n\n"
        f"Laman voting: {vote_link}\n"
        f"Batas waktu: {vote_deadline}\n\n"
        f"Penting:\n"
        f"- Token unik & rahasia (satu pemilih satu suara)\n"
        f"- Jangan bagikan token ke siapa pun\n"
        f"- Email terdaftar: {email}\n\n"
        f"Jika ada kendala: {support_email or settings.SUPPORT_EMAIL}\n"
        f"© {election_year} KPU PPI Osaka–Nara\n"
    )
    return text
