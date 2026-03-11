<template>
  <div class="page">
    <div class="stats">
      <div class="stat-card">
        <div class="stat-value">{{ tasks.length }}</div>
        <div class="stat-label">全部任务</div>
      </div>
      <div class="stat-card stat-pending">
        <div class="stat-value">{{ pendingTasks.length }}</div>
        <div class="stat-label">待执行</div>
      </div>
      <div class="stat-card stat-done">
        <div class="stat-value">{{ completedTasks.length }}</div>
        <div class="stat-label">已完成</div>
      </div>
      <div class="stat-card stat-immediate">
        <div class="stat-value">{{ immediateTasks.length }}</div>
        <div class="stat-label">立即执行</div>
      </div>
    </div>
    <div class="toolbar">
      <div class="tabs">
        <button :class="['tab', { active: filter === 'all' }]" @click="filter = 'all'">
          全部 <span class="tab-count">{{ tasks.length }}</span>
        </button>
        <button :class="['tab', { active: filter === 'pending' }]" @click="filter = 'pending'">
          待执行 <span class="tab-count">{{ pendingTasks.length }}</span>
        </button>
        <button :class="['tab', { active: filter === 'completed' }]" @click="filter = 'completed'">
          已完成 <span class="tab-count">{{ completedTasks.length }}</span>
        </button>
      </div>
      <router-link to="/add" class="btn-add">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        新建任务
      </router-link>
    </div>
    <div class="task-list" v-if="filteredTasks.length">
      <div v-for="task in filteredTasks" :key="task.id" class="task-row" :class="{ done: task.completed }">
        <div class="task-left">
          <button class="check-btn" :class="{ checked: task.completed }" @click="toggleDone(task)">
            <svg v-if="task.completed" width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 7l3 3 5-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <div class="task-info">
            <div class="task-name-row">
              <router-link :to="'/task/' + task.id" class="task-name">{{ task.title }}</router-link>
              <span v-if="task.immediately" class="tag tag-orange">立即</span>
              <span v-if="task.is_send" class="tag tag-blue">推送</span>
            </div>
            <div class="task-meta">
              <span v-if="task.description" class="meta-desc">{{ task.description }}</span>
              <span class="meta-time">{{ task.time }}</span>
              <span v-if="task.trigger_count > 0" class="meta-trigger">已触发 {{ task.trigger_count }} 次</span>
              <span v-if="task.trigger_time_list && task.trigger_time_list.length > 0" class="meta-rules">{{ task.trigger_time_list.length }} 条规则</span>
            </div>
          </div>
        </div>
        <div class="task-right">
          <router-link :to="'/edit/' + task.id" class="action-btn action-edit" title="编辑">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M11.5 2.5l2 2L5 13H3v-2l8.5-8.5z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </router-link>
          <router-link :to="'/task/' + task.id" class="action-btn" title="查看详情">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M6 3l5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </router-link>
          <button class="action-btn action-delete" title="删除" @click="confirmDelete(task)">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </button>
        </div>
      </div>
    </div>
    <div v-else class="empty">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none"><rect x="12" y="8" width="40" height="48" rx="4" stroke="#cbd5e1" stroke-width="2"/><path d="M22 24h20M22 32h14M22 40h18" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round"/></svg>
      <p class="empty-title">暂无任务</p>
      <p class="empty-hint">点击右上角「新建任务」开始</p>
    </div>
    <div v-if="showDeleteConfirm" class="overlay" @click.self="showDeleteConfirm = false">
      <div class="confirm-box">
        <p class="confirm-text">确定删除此任务吗？</p>
        <div class="confirm-actions">
          <button class="btn btn-cancel" @click="showDeleteConfirm = false">取消</button>
          <button class="btn btn-del" @click="deleteTask">删除</button>
        </div>
      </div>
    </div>
    <transition name="slide-up">
      <div v-if="toast.show" :class="['toast', 'toast-' + toast.type]">{{ toast.message }}</div>
    </transition>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'MainPage',
  data: function () {
    return {
      tasks: [],
      filter: 'all',
      showDeleteConfirm: false,
      deleteTarget: null,
      toast: { show: false, message: '', type: 'ok' }
    }
  },
  computed: {
    pendingTasks: function () { return this.tasks.filter(function (t) { return !t.completed }) },
    completedTasks: function () { return this.tasks.filter(function (t) { return t.completed }) },
    immediateTasks: function () { return this.tasks.filter(function (t) { return t.immediately && !t.completed }) },
    filteredTasks: function () {
      if (this.filter === 'pending') return this.pendingTasks
      if (this.filter === 'completed') return this.completedTasks
      return this.tasks
    }
  },
  mounted: function () {
    this.fetchAll()
    var self = this
    this._timer = setInterval(function () { self.fetchAll() }, 30000)
  },
  beforeUnmount: function () { clearInterval(this._timer) },
  methods: {
    fetchAll: function () {
      var self = this
      return axios.get('/api/tasks').then(function (res) {
        if (res.data.status === 'ok') self.tasks = res.data.tasks
      }).catch(function () {})
    },
    toggleDone: function (task) {
      var self = this
      var url = task.completed ? '/api/set_undone/' + task.id : '/api/set_done/' + task.id
      return axios.get(url).then(function (res) {
        if (res.data.status === 'ok') {
          self.tip(task.completed ? '已恢复' : '已完成')
          return self.fetchAll()
        } else {
          self.tip(res.data.message, 'err')
        }
      }).catch(function () { self.tip('操作失败', 'err') })
    },
    confirmDelete: function (task) {
      this.deleteTarget = task
      this.showDeleteConfirm = true
    },
    deleteTask: function () {
      if (!this.deleteTarget) return
      var self = this
      return axios.get('/api/delete_task/' + this.deleteTarget.id).then(function (res) {
        if (res.data.status === 'ok') {
          self.tip('已删除')
          self.showDeleteConfirm = false
          self.deleteTarget = null
          return self.fetchAll()
        } else {
          self.tip(res.data.message, 'err')
        }
      }).catch(function () { self.tip('删除失败', 'err') })
    },
    tip: function (msg, type) {
      this.toast = { show: true, message: msg, type: type || 'ok' }
      var self = this
      setTimeout(function () { self.toast.show = false }, 2500)
    }
  }
}
</script>

<style scoped>
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 28px; }
.stat-card { background: #fff; border: 1px solid #eef0f4; border-radius: 10px; padding: 18px 20px; text-align: center; }
.stat-value { font-size: 30px; font-weight: 700; color: #1a1a2e; line-height: 1.2; }
.stat-label { font-size: 12px; color: #8892a4; margin-top: 4px; letter-spacing: 0.5px; }
.stat-pending { border-left: 3px solid #6366f1; }
.stat-done { border-left: 3px solid #22c55e; }
.stat-immediate { border-left: 3px solid #f59e0b; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.tabs { display: flex; gap: 2px; background: #f1f3f7; border-radius: 8px; padding: 3px; }
.tab { padding: 7px 16px; border: none; background: transparent; color: #64748b; font-size: 13px; font-weight: 500; border-radius: 6px; cursor: pointer; transition: all 0.15s; display: flex; align-items: center; gap: 6px; }
.tab.active { background: #fff; color: #1a1a2e; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.tab:hover:not(.active) { color: #334155; }
.tab-count { background: #e8ebf0; color: #64748b; font-size: 11px; padding: 1px 7px; border-radius: 10px; font-weight: 600; }
.tab.active .tab-count { background: #6366f1; color: #fff; }
.btn-add { display: inline-flex; align-items: center; gap: 6px; padding: 8px 18px; background: #6366f1; color: #fff; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; text-decoration: none; cursor: pointer; transition: background 0.15s; }
.btn-add:hover { background: #4f46e5; }
.task-list { display: flex; flex-direction: column; gap: 1px; background: #eef0f4; border: 1px solid #eef0f4; border-radius: 10px; overflow: hidden; }
.task-row { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; background: #fff; transition: background 0.1s; }
.task-row:hover { background: #fafbfc; }
.task-row.done { opacity: 0.55; }
.task-left { display: flex; align-items: flex-start; gap: 12px; flex: 1; min-width: 0; }
.check-btn { width: 22px; height: 22px; min-width: 22px; border: 2px solid #cbd5e1; border-radius: 6px; background: transparent; cursor: pointer; display: flex; align-items: center; justify-content: center; margin-top: 2px; transition: all 0.15s; color: #fff; }
.check-btn:hover { border-color: #6366f1; }
.check-btn.checked { background: #22c55e; border-color: #22c55e; }
.task-info { flex: 1; min-width: 0; }
.task-name-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.task-name { font-size: 14px; font-weight: 600; color: #1a1a2e; text-decoration: none; transition: color 0.1s; }
.task-name:hover { color: #6366f1; }
.done .task-name { text-decoration: line-through; color: #94a3b8; }
.tag { font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 4px; letter-spacing: 0.3px; text-transform: uppercase; }
.tag-orange { background: #fef3c7; color: #b45309; }
.tag-blue { background: #dbeafe; color: #1d4ed8; }
.task-meta { display: flex; gap: 12px; margin-top: 4px; flex-wrap: wrap; }
.task-meta span { font-size: 12px; color: #8892a4; }
.meta-desc { max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.task-right { display: flex; align-items: center; gap: 4px; margin-left: 12px; }
.action-btn { width: 30px; height: 30px; border: none; background: transparent; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #94a3b8; transition: all 0.1s; text-decoration: none; }
.action-btn:hover { background: #f1f3f7; color: #475569; }
.action-edit:hover { background: #eef2ff; color: #6366f1; }
.action-delete:hover { background: #fef2f2; color: #ef4444; }
.empty { text-align: center; padding: 64px 20px; }
.empty-title { font-size: 16px; font-weight: 600; color: #475569; margin: 20px 0 6px; }
.empty-hint { font-size: 13px; color: #94a3b8; margin: 0; }
.overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 500; }
.confirm-box { background: #fff; border-radius: 12px; padding: 28px; width: 380px; max-width: 90vw; box-shadow: 0 20px 40px rgba(0,0,0,0.12); }
.confirm-text { font-size: 14px; color: #334155; margin: 0 0 20px; line-height: 1.6; }
.confirm-actions { display: flex; gap: 10px; justify-content: flex-end; }
.btn { padding: 8px 18px; border-radius: 7px; border: none; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s; }
.btn-cancel { background: #f1f3f7; color: #475569; }
.btn-cancel:hover { background: #e2e5ea; }
.btn-del { background: #ef4444; color: #fff; }
.btn-del:hover { background: #dc2626; }
.toast { position: fixed; bottom: 28px; left: 50%; transform: translateX(-50%); padding: 10px 24px; border-radius: 8px; font-size: 13px; font-weight: 500; z-index: 600; box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.toast-ok { background: #1a1a2e; color: #fff; }
.toast-err { background: #ef4444; color: #fff; }
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.25s ease; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateX(-50%) translateY(12px); }
@media (max-width: 640px) {
  .stats { grid-template-columns: repeat(2, 1fr); }
  .toolbar { flex-direction: column; gap: 12px; align-items: stretch; }
  .btn-add { justify-content: center; }
}
</style>
