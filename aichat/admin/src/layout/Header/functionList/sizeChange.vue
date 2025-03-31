<template>
  <el-dropdown @command="handleCommand"
               size="medium">
    <span class="el-dropdown-link">
      <i class="sfont system-zuixiaohua"></i>
    </span>
    <template #dropdown>
      <el-dropdown-menu>

      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script lang="js">
import { defineComponent, computed, unref } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from 'vuex'
export default defineComponent({
  setup() {
    const store = useStore()
    const route = useRoute()
    const list = [
      { size: 'large', name: '大' },
      { size: 'default', name: '默认' },
      { size: 'small', name: '小' },
    ]
    const { fullPath } = unref(route)
    return {
      list,
      fullPath
    }
  },
  methods: {

  }
})
</script>

<style lang="scss" scoped>
</style>