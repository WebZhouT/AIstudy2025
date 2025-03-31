<template>
  <div class="logo-container">
    logo
    <!-- <h1 v-if="!isCollapse">{{ systemTitle }}</h1> -->
  </div>
</template>

<script lang="js">
import { defineComponent, computed } from 'vue'
import { useStore } from 'vuex'
import { systemTitle } from '@/config'
export default defineComponent({
  setup() {
    const store = useStore()
    const isCollapse = computed(() => store.state.app.isCollapse)
    return {
      isCollapse,
      systemTitle
    }
  }
})
</script>

<style lang="scss" scoped>
.logo-container {
  background: #fff;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  img {
    height: 30px;
  }
  h1 {
    font-size: 18px;
    white-space: nowrap;
    color: #333;
  }
}
</style>