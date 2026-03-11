<template>
  <div class="page">
    <div class="page-header">
      <router-link to="/" class="back-link">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 3L5 8l5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        返回列表
      </router-link>
      <h2 class="page-title">新建任务</h2>
    </div>

    <form class="form-card" @submit.prevent="submit">
      <!-- 基本信息 -->
      <section class="form-section">
        <h3 class="section-title">基本信息</h3>
        <div class="field">
          <label class="field-label">任务标题 <span class="req">*</span></label>
          <input v-model="form.title" type="text" class="input" placeholder="输入任务标题" />
        </div>
        <div class="field">
          <label class="field-label">任务描述</label>
          <textarea v-model="form.description" class="input textarea" placeholder="输入任务描述（可选）" rows="3"></textarea>
        </div>
      </section>

      <!-- 执行代码 -->
      <section class="form-section">
        <h3 class="section-title">执行代码 <span class="req">*</span></h3>
        <div class="code-editor">
          <div class="code-header">
            <span class="code-lang">Python</span>
          </div>
          <div class="code-body">
            <textarea
              ref="codeInput"
              v-model="form.code"
              class="code-input"
              placeholder="def run():&#10;    return 'Hello World'"
              rows="10"
              spellcheck="false"
              @input="updateHighlight"
              @scroll="syncScroll"
            ></textarea>
            <pre class="code-highlight" ref="codeHighlight"><code v-html="highlightedCode"></code></pre>
          </div>
        </div>
      </section>

      <!-- 执行设置 -->
      <section class="form-section">
        <h3 class="section-title">执行设置</h3>
        <div class="field-row">
          <label class="toggle-label">
            <input type="checkbox" v-model="form.immediately" class="toggle-input" />
            <span class="toggle-switch"></span>
            <span class="toggle-text">立即执行</span>
          </label>
          <div class="field field-inline">
            <label class="field-label">目标执行次数</label>
            <input v-model.number="form.target_count" type="number" class="input input-sm" min="0" placeholder="0 = 不限" />
          </div>
        </div>
      </section>

      <!-- 触发规则 -->
      <section class="form-section">
        <h3 class="section-title">触发规则</h3>
        <div v-for="(trigger, i) in form.triggers" :key="i" class="trigger-card">
          <div class="trigger-top">
            <span class="trigger-num">规则 #{{ i + 1 }}</span>
            <button type="button" class="btn-icon btn-remove" @click="removeTrigger(i)">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M3 3l8 8M11 3l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <div class="trigger-grid">
            <div class="field">
              <label class="field-label-sm">月份 <span class="hint">如 1,2,3</span></label>
              <input v-model="trigger.mouthStr" type="text" class="input" placeholder="留空=每月" />
            </div>
            <div class="field">
              <label class="field-label-sm">星期 <span class="hint">0=周一 6=周日</span></label>
              <input v-model="trigger.weekDayStr" type="text" class="input" placeholder="留空=每天" />
            </div>
            <div class="field">
              <label class="field-label-sm">日期</label>
              <input v-model="trigger.mouthDayStr" type="text" class="input" placeholder="留空=每天" />
            </div>
            <div class="field-row-inner">
              <div class="field">
                <label class="field-label-sm">小时</label>
                <input v-model.number="trigger.hour" type="number" class="input" min="0" max="23" />
              </div>
              <div class="field">
                <label class="field-label-sm">分钟</label>
                <input v-model.number="trigger.minute" type="number" class="input" min="0" max="59" />
              </div>
            </div>
          </div>
        </div>
        <button type="button" class="btn-add-trigger" @click="addTrigger">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 2v10M2 7h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
          添加触发规则
        </button>
      </section>

      <!-- 消息推送 -->
      <section class="form-section">
        <h3 class="section-title">消息推送</h3>
        <label class="toggle-label">
          <input type="checkbox" v-model="form.is_send" class="toggle-input" />
          <span class="toggle-switch"></span>
          <span class="toggle-text">启用推送</span>
        </label>
        <div v-if="form.is_send" class="send-fields">
          <div class="field">
            <label class="field-label">推送 URL</label>
            <input v-model="form.send_url" type="text" class="input" placeholder="https://example.com/send" />
          </div>
          <div class="field">
            <label class="field-label">Token</label>
            <input v-model="form.send_token" type="text" class="input" placeholder="输入 Token" />
          </div>
        </div>
      </section>

      <!-- 提交 -->
      <div class="form-footer">
        <router-link to="/" class="btn btn-cancel">取消</router-link>
        <button type="submit" class="btn btn-submit" :disabled="submitting">
          {{ submitting ? '提交中...' : '创建任务' }}
        </button>
      </div>
    </form>

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
  name: 'AddTask',
  data() {
    return {
      form: {
        title: '',
        description: '',
        code: '',
        immediately: false,
        target_count: 0,
        triggers: [],
        is_send: false,
        send_url: '',
        send_token: ''
      },
      submitting: false,
      highlightedCode: '',
      toast: { show: false, message: '', type: 'ok' }
    }
  },
  mounted() {
    this.updateHighlight()
  },
  methods: {
    updateHighlight() {
      const code = this.form.code || ' '
      this.highlightedCode = hljs.highlight(code, { language: 'python' }).value
    },
    syncScroll() {
      const textarea = this.$refs.codeInput
      const pre = this.$refs.codeHighlight
      if (textarea && pre) {
        pre.scrollTop = textarea.scrollTop
        pre.scrollLeft = textarea.scrollLeft
      }
    },
    addTrigger() {
      this.form.triggers.push({
        mouthStr: '',
        weekDayStr: '',
        mouthDayStr: '',
        hour: 0,
        minute: 0
      })
    },
    removeTrigger(i) {
      this.form.triggers.splice(i, 1)
    },
    parseIntList(str) {
      if (!str || !str.trim()) return []
      return str.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n))
    },
    tip(msg, type = 'ok') {
      this.toast = { show: true, message: msg, type }
      setTimeout(() => { this.toast.show = false }, 3000)
    },
    async submit() {
      if (!this.form.title.trim()) return this.tip('请输入任务标题', 'err')
      if (!this.form.code.trim()) return this.tip('请输入执行代码', 'err')
      if (!this.form.immediately && this.form.triggers.length === 0) {
        return this.tip('请选择「立即执行」或添加触发规则', 'err')
      }

      this.submitting = true
      try {
        const payload = {
          title: this.form.title,
          description: this.form.description,
          code: this.form.code,
          immediately: this.form.immediately,
          target_count: this.form.target_count || 0,
          is_send: this.form.is_send,
          send_url: this.form.send_url,
          send_token: this.form.send_token,
          trigger_time_list: this.form.triggers.map(t => ({
            mouth: this.parseIntList(t.mouthStr),
            week_day: this.parseIntList(t.weekDayStr),
            mouth_day: this.parseIntList(t.mouthDayStr),
            day_time: [t.hour || 0, t.minute || 0]
          }))
        }

        const { data } = await axios.post(`${API}/add_task`, payload)
        if (data.status === 'ok') {
          this.tip('任务创建成功')
          setTimeout(() => this.$router.push('/'), 800)
        } else {
          this.tip('创建失败: ' + data.message, 'err')
        }
      } catch (e) {
        void e
        this.tip('网络错误', 'err')
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
.page-header {
  margin-bottom: 24px;
}
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
  margin-bottom: 8px;
}
.back-link:hover { color: #4f46e5; }
.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}

/* ===== 表单卡片 ===== */
.form-card {
  background: #fff;
  border: 1px solid #eef0f4;
  border-radius: 12px;
  overflow: hidden;
}

.form-section {
  padding: 24px 28px;
  border-bottom: 1px solid #f1f3f7;
}
.form-section:last-of-type { border-bottom: none; }

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 16px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ===== 字段 ===== */
.field { margin-bottom: 14px; }
.field:last-child { margin-bottom: 0; }

.field-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 6px;
}
.field-label-sm {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 4px;
}
.req { color: #ef4444; }
.hint { color: #94a3b8; font-weight: 400; }

.input {
  width: 100%;
  padding: 9px 12px;
  border: 1px solid #e2e5ea;
  border-radius: 7px;
  font-size: 14px;
  color: #1a1a2e;
  background: #fafbfc;
  transition: border-color .15s, box-shadow .15s;
  box-sizing: border-box;
  font-family: inherit;
}
.input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, .1);
  background: #fff;
}
.input::placeholder { color: #b0b8c4; }
.textarea { resize: vertical; }
.input-sm { width: 120px; }

.field-row {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}
.field-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 0;
}
.field-inline .field-label { margin-bottom: 0; white-space: nowrap; }

/* ===== Toggle ===== */
.toggle-label {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}
.toggle-input { display: none; }
.toggle-switch {
  width: 36px;
  height: 20px;
  background: #d1d5db;
  border-radius: 10px;
  position: relative;
  transition: background .2s;
}
.toggle-switch::after {
  content: '';
  width: 16px;
  height: 16px;
  background: #fff;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform .2s;
  box-shadow: 0 1px 3px rgba(0,0,0,.1);
}
.toggle-input:checked + .toggle-switch { background: #6366f1; }
.toggle-input:checked + .toggle-switch::after { transform: translateX(16px); }
.toggle-text {
  font-size: 13px;
  font-weight: 500;
  color: #475569;
}

/* ===== 代码编辑器 ===== */
.code-editor {
  border: 1px solid #e2e5ea;
  border-radius: 8px;
  overflow: hidden;
}
.code-header {
  background: #1e293b;
  padding: 6px 14px;
  display: flex;
  align-items: center;
}
.code-lang {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .5px;
}
.code-body {
  position: relative;
  background: #0d1117;
}
.code-input,
.code-highlight {
  font-family: 'Fira Code', 'Cascadia Code', 'JetBrains Mono', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.7;
  padding: 16px;
  margin: 0;
  border: none;
  white-space: pre;
  overflow: auto;
  tab-size: 4;
}
.code-input {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  min-height: 200px;
  color: transparent;
  caret-color: #e2e8f0;
  background: transparent;
  resize: vertical;
  box-sizing: border-box;
}
.code-input:focus { outline: none; }
.code-highlight {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  pointer-events: none;
  color: #e2e8f0;
  background: transparent;
}
.code-highlight code {
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
}

/* ===== 触发规则 ===== */
.trigger-card {
  background: #fafbfc;
  border: 1px solid #eef0f4;
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 10px;
}
.trigger-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.trigger-num {
  font-size: 12px;
  font-weight: 700;
  color: #6366f1;
  text-transform: uppercase;
  letter-spacing: .3px;
}
.btn-icon {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  transition: all .1s;
}
.btn-remove:hover { background: #fef2f2; color: #ef4444; }

.trigger-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.field-row-inner {
  display: flex;
  gap: 10px;
}
.field-row-inner .field { flex: 1; }

.btn-add-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px;
  border: 1px dashed #d1d5db;
  border-radius: 8px;
  background: transparent;
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all .15s;
}
.btn-add-trigger:hover {
  border-color: #6366f1;
  color: #6366f1;
  background: #f5f3ff;
}

/* ===== 推送设置 ===== */
.send-fields {
  margin-top: 14px;
  padding: 14px 16px;
  background: #fafbfc;
  border: 1px solid #eef0f4;
  border-radius: 8px;
}

/* ===== 底部操作 ===== */
.form-footer {
  padding: 18px 28px;
  background: #fafbfc;
  border-top: 1px solid #f1f3f7;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.btn {
  padding: 9px 22px;
  border-radius: 8px;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  transition: all .15s;
}
.btn-cancel {
  background: #f1f3f7;
  color: #475569;
}
.btn-cancel:hover { background: #e2e5ea; }
.btn-submit {
  background: #6366f1;
  color: #fff;
}
.btn-submit:hover:not(:disabled) { background: #4f46e5; }
.btn-submit:disabled { opacity: .6; cursor: not-allowed; }

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

/* ===== 响应式 ===== */
@media (max-width: 640px) {
  .form-section { padding: 18px 16px; }
  .trigger-grid { grid-template-columns: 1fr; }
  .field-row { flex-direction: column; gap: 12px; }
  .form-footer { padding: 14px 16px; }
}
</style>
