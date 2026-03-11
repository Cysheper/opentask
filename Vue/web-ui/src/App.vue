<template>
  <div id="app">
    <!-- 顶部导航 -->
    <header class="nav">
      <router-link to="/" class="nav-brand">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <rect x="2" y="2" width="16" height="16" rx="3" stroke="currentColor" stroke-width="1.5"/>
          <path d="M6 10l3 3 5-6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Task Manager
      </router-link>
      <div class="nav-right">
        <span class="health" :class="healthCls">
          <span class="health-dot"></span>
          {{ healthLabel }}
        </span>
      </div>
    </header>
    <!-- 页面内容 -->
    <div class="container">
      <router-view />
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      healthCls: 'h-unknown',
      healthLabel: '检测中...'
    }
  },
  mounted() {
    this.checkHealth()
    this._ht = setInterval(() => this.checkHealth(), 60000)
  },
  beforeUnmount() { clearInterval(this._ht) },
  methods: {
    async checkHealth() {
      try {
        const { data } = await axios.get('/api/health')
        if (data.status === 'ok') {
          this.healthCls = 'h-ok'
          this.healthLabel = '服务正常'
        } else {
          this.healthCls = 'h-err'
          this.healthLabel = '服务异常'
        }
      } catch (e) {
        void e
        this.healthCls = 'h-err'
        this.healthLabel = '连接失败'
      }
    }
  }
}
</script>

<style>
/* ===== 重置 ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans SC', 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  background: #f6f7f9;
  color: #1a1a2e;
}
#app { min-height: 100vh; }

/* ===== 导航 ===== */
.nav {
  height: 52px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #eef0f4;
  position: sticky;
  top: 0;
  z-index: 100;
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #1a1a2e;
  text-decoration: none;
  letter-spacing: -.3px;
}
.nav-right {
  display: flex;
  align-items: center;
}
.health {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
}
.health-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #cbd5e1;
}
.h-ok .health-dot { background: #22c55e; box-shadow: 0 0 4px #22c55e; }
.h-ok { color: #16a34a; }
.h-err .health-dot { background: #ef4444; box-shadow: 0 0 4px #ef4444; }
.h-err { color: #ef4444; }
.h-unknown .health-dot { background: #fbbf24; animation: blink 1.2s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ===== 内容容器 ===== */
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 28px 20px;
}
</style>
