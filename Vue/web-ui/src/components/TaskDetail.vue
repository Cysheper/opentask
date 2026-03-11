<template>
  <div class="page">
    <div class="page-header">
      <router-link to="/" class="back-link">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回列表
      </router-link>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="task" class="detail-card">
      <!-- 标题栏 -->
      <div class="detail-top">
        <div class="detail-title-row">
          <span class="task-id">#{{ task.id }}</span>
          <h2 class="detail-title">{{ task.title }}</h2>
          <span :class="['status-badge', task.completed ? 'status-done' : 'status-active']">
            {{ task.completed ? '已完成' : '进行中' }}
          </span>
        </div>
        <div class="detail-actions">
          <router-link :to="'/edit/' + task.id" class="btn btn-edit">✎ 编辑</router-link>
          <button
            v-if="!task.completed"
            class="btn btn-done"
            @click="setDone"
          >✓ 标记完成</button>
          <button
            v-else
            class="btn btn-undo"
            @click="setUndone"
          >↩ 恢复执行</button>
          <button class="btn btn-del" @click="showDeleteConfirm = true">删除</button>
        </div>
      </div>

      <!-- 信息网格 -->
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">描述</span>
          <span class="info-value">{{ task.description || '—' }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">创建时间</span>
          <span class="info-value">{{ task.time }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">立即执行</span>
          <span class="info-value">
            <span :class="['inline-tag', task.immediately ? 'tag-yes' : 'tag-no']">
              {{ task.immediately ? '是' : '否' }}
            </span>
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">触发次数</span>
          <span class="info-value">
            {{ task.trigger_count }}{{ task.target_count > 0 ? ' / ' + task.target_count : '' }}
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">消息推送</span>
          <span class="info-value">
            <span :class="['inline-tag', task.is_send ? 'tag-yes' : 'tag-no']">
              {{ task.is_send ? '已启用' : '未启用' }}
            </span>
          </span>
        </div>
        <div class="info-item" v-if="task.is_send">
          <span class="info-label">推送 URL</span>
          <span class="info-value url-value">{{ task.send_url }}</span>
        </div>
      </div>

      <!-- 触发规则 -->
      <div class="detail-section">
        <h3 class="section-title">触发规则</h3>
        <div v-if="task.trigger_time_list && task.trigger_time_list.length > 0" class="rules-list">
          <div v-for="(tr, i) in task.trigger_time_list" :key="i" class="rule-item">
            <span class="rule-num">#{{ i + 1 }}</span>
            <div class="rule-tags">
              <span v-if="tr.mouth && tr.mouth.length" class="rule-tag">月: {{ tr.mouth.join(', ') }}</span>
              <span v-if="tr.week_day && tr.week_day.length" class="rule-tag">周: {{ tr.week_day.map(d => weekDays[d]).join(', ') }}</span>
              <span v-if="tr.mouth_day && tr.mouth_day.length" class="rule-tag">日: {{ tr.mouth_day.join(', ') }}</span>
              <span v-if="tr.day_time" class="rule-tag">
                {{ String(tr.day_time[0]).padStart(2,'0') }}:{{ String(tr.day_time[1]).padStart(2,'0') }}
              </span>
            </div>
          </div>
        </div>
        <p v-else class="no-data">无触发规则</p>
      </div>

      <!-- 代码 -->
      <div class="detail-section">
        <h3 class="section-title">执行代码</h3>
        <div class="code-block">
          <div class="code-block-header">
            <span class="code-block-lang">Python</span>
          </div>
          <pre class="code-block-body"><code v-html="highlightedCode"></code></pre>
        </div>
      </div>
    </div>

    <div v-else class="not-found">
      <p>任务不存在</p>
      <router-link to="/" class="back-link">返回列表</router-link>
    </div>

    <!-- 删除确认 -->
    <div class="overlay" v-if="showDeleteConfirm" @click.self="showDeleteConfirm = false">
      <div class="confirm-box">
        <p class="confirm-text">确定删除任务 <strong>「{{ task?.title }}」</strong>？</p>
        <div class="confirm-actions">
          <button class="btn btn-cancel" @click="showDeleteConfirm = false">取消</button>
          <button class="btn btn-del" @click="deleteTask">确认删除</button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <transition name="slide-up">
      <div v-if="toast.show" :class="['toast', 'toast-' + toast.type]">
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script>
import axios from 'axios'
import hljs from 'highlight.js/lib/core'
import python from 'highlight.js/lib/languages/python'
import 'highlight.js/styles/github-dark.css'

hljs.registerLanguage('python', python)

const API = '/api'

export default {
  name: 'TaskDetail',
  props: ['id'],
  data() {
    return {
      task: null,
      loading: true,
      showDeleteConfirm: false,
      weekDays: ['一', '二', '三', '四', '五', '六', '日'],
      toast: { show: false, message: '', type: 'ok' }
    }
  },
  computed: {
    highlightedCode() {
      if (!this.task?.code) return ''
      return hljs.highlight(this.task.code, { language: 'python' }).value
    }
  },
  mounted() {
    this.fetch()
  },
  methods: {
    async fetch() {
      this.loading = true
      try {
        const { data } = await axios.get(`${API}/tasks`)
        if (data.status === 'ok') {
          this.task = data.tasks.find(t => t.id === Number(this.id)) || null
        }
      } catch (e) { void e }
      this.loading = false
    },
    async setDone() {
      try {
        const { data } = await axios.get(`${API}/set_done/${this.task.id}`)
        if (data.status === 'ok') {
          this.tip('已标记完成')
          await this.fetch()
        }
      } catch (e) { void e; this.tip('操作失败', 'err') }
    },
    async setUndone() {
      try {
        const { data } = await axios.get(`${API}/set_undone/${this.task.id}`)
        if (data.status === 'ok') {
          this.tip('已恢复')
          await this.fetch()
        }
      } catch (e) { void e; this.tip('操作失败', 'err') }
    },
    async deleteTask() {
      try {
        const { data } = await axios.get(`${API}/delete_task/${this.task.id}`)
        if (data.status === 'ok') {
          this.tip('已删除')
          setTimeout(() => this.$router.push('/'), 600)
        }
      } catch (e) { void e; this.tip('删除失败', 'err') }
    },
    tip(msg, type = 'ok') {
      this.toast = { show: true, message: msg, type }
      setTimeout(() => { this.toast.show = false }, 2500)
    }
  }
}
</script>

<style scoped>
.page-header { margin-bottom: 20px; }
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
}
.back-link:hover { color: #4f46e5; }

.loading, .not-found {
  text-align: center;
  padding: 60px;
  color: #64748b;
  font-size: 14px;
}

/* ===== 详情卡片 ===== */
.detail-card {
  background: #fff;
  border: 1px solid #eef0f4;
  border-radius: 12px;
  overflow: hidden;
}

.detail-top {
  padding: 24px 28px;
  border-bottom: 1px solid #f1f3f7;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}
.detail-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.task-id {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
}
.detail-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}
.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: .3px;
}
.status-active { background: #ede9fe; color: #6d28d9; }
.status-done { background: #dcfce7; color: #16a34a; }

.detail-actions {
  display: flex;
  gap: 8px;
}
.btn {
  padding: 8px 16px;
  border-radius: 7px;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all .15s;
}
.btn-done { background: #22c55e; color: #fff; }
.btn-done:hover { background: #16a34a; }
.btn-edit { background: #6366f1; color: #fff; text-decoration: none; }
.btn-edit:hover { background: #4f46e5; }
.btn-undo { background: #f59e0b; color: #fff; }
.btn-undo:hover { background: #d97706; }
.btn-del { background: #ef4444; color: #fff; }
.btn-del:hover { background: #dc2626; }
.btn-cancel { background: #f1f3f7; color: #475569; }
.btn-cancel:hover { background: #e2e5ea; }

/* ===== 信息网格 ===== */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  padding: 0;
}
.info-item {
  padding: 16px 28px;
  border-bottom: 1px solid #f1f3f7;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.info-item:nth-child(odd) { border-right: 1px solid #f1f3f7; }
.info-label {
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: .5px;
}
.info-value {
  font-size: 14px;
  color: #1a1a2e;
}
.url-value { word-break: break-all; font-size: 13px; color: #64748b; }

.inline-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}
.tag-yes { background: #dcfce7; color: #16a34a; }
.tag-no { background: #f1f3f7; color: #94a3b8; }

/* ===== 区块 ===== */
.detail-section {
  padding: 24px 28px;
  border-bottom: 1px solid #f1f3f7;
}
.detail-section:last-child { border-bottom: none; }
.section-title {
  font-size: 13px;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: .5px;
  margin: 0 0 14px;
}

/* 规则 */
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.rule-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: #fafbfc;
  border: 1px solid #eef0f4;
  border-radius: 8px;
}
.rule-num {
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
}
.rule-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.rule-tag {
  font-size: 12px;
  color: #475569;
  background: #f1f3f7;
  padding: 3px 8px;
  border-radius: 4px;
}
.no-data {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

/* ===== 代码块 ===== */
.code-block {
  border: 1px solid #e2e5ea;
  border-radius: 8px;
  overflow: hidden;
}
.code-block-header {
  background: #1e293b;
  padding: 6px 14px;
}
.code-block-lang {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .5px;
}
.code-block-body {
  background: #0d1117;
  padding: 16px;
  margin: 0;
  overflow-x: auto;
}
.code-block-body code {
  font-family: 'Fira Code', 'Cascadia Code', 'JetBrains Mono', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #e6edf3;
}

/* ===== 弹窗 ===== */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, .4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 500;
}
.confirm-box {
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  width: 380px;
  max-width: 90vw;
  box-shadow: 0 20px 40px rgba(0,0,0,.12);
}
.confirm-text {
  font-size: 14px;
  color: #334155;
  margin: 0 0 20px;
  line-height: 1.6;
}
.confirm-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* ===== Toast ===== */
.toast {
  position: fixed;
  bottom: 28px;
  left: 50%;
  transform: translateX(-50%);
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  z-index: 600;
  box-shadow: 0 8px 24px rgba(0,0,0,.12);
}
.toast-ok { background: #1a1a2e; color: #fff; }
.toast-err { background: #ef4444; color: #fff; }
.slide-up-enter-active, .slide-up-leave-active { transition: all .25s ease; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }

@media (max-width: 640px) {
  .detail-top { flex-direction: column; padding: 18px 16px; }
  .info-grid { grid-template-columns: 1fr; }
  .info-item:nth-child(odd) { border-right: none; }
  .detail-section { padding: 18px 16px; }
}
</style>
