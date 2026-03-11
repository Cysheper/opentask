import { createRouter, createWebHistory } from 'vue-router'
import MainPage from '../components/MainPage.vue'
import AddTask from '../components/AddTask.vue'
import TaskDetail from '../components/TaskDetail.vue'
import EditTask from '../components/EditTask.vue'

const routes = [
  { path: '/', name: 'Home', component: MainPage },
  { path: '/add', name: 'AddTask', component: AddTask },
  { path: '/task/:id', name: 'TaskDetail', component: TaskDetail, props: true },
  { path: '/edit/:id', name: 'EditTask', component: EditTask, props: true }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
