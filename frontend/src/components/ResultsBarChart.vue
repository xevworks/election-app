<template>
  <div style="padding:8px 0">
    <div v-for="d in data" :key="d.candidate_id" style="margin:10px 0">
      <div style="font-weight:600">{{ d.candidate_name }}</div>
      <div style="background:#e9ecf3;height:8px;border-radius:4px;overflow:hidden">
        <div :style="{width: ((d.votes/max)*100)+'%'}" style="height:8px;background:#2260ff"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({ data: { type: Array, default: () => [] } })
const max = Math.max(1, ...props.data.map(d => d.votes||0))
</script>