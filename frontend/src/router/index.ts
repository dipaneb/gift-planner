import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/stores/auth";

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    guestOnly?: boolean
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/LoginView.vue"),
    meta: { guestOnly: true },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("@/views/RegisterView.vue"),
    meta: { guestOnly: true },
  },
  {
    path: "/forgot-password",
    name: "forgotPassword",
    component: () => import("@/views/ForgotPasswordView.vue"),
    meta: { guestOnly: true },
  },
  {
    path: "/reset-password",
    name: "resetPassword",
    component: () => import("@/views/ResetPasswordView.vue"),
    meta: { guestOnly: true },
  },
  {
    path: "",
    component: () => import("@/layouts/AuthLayout.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "app",
        name: "dashboard",
        component: () => import("@/views/DashboardView.vue"),
      },
      {
        path: "profile",
        name: "profile",
        component: () => import("@/views/ProfileView.vue"),
      },
      {
        path: "settings",
        name: "settings",
        component: () => import("@/views/SettingsView.vue"),
      },
    ],
  },
  {
    path: "/",
    redirect: "/app",
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, from) => {
  const authStore = useAuthStore();

  // Initialize auth state on first navigation
  if (!authStore.isInitialized && !authStore.isInitializing) {
    await authStore.initialize();
  }

  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const guestOnly = to.matched.some((record) => record.meta.guestOnly);
  const isAuthenticated = authStore.isAuthenticated;

  if (requiresAuth && !isAuthenticated) {
    // Redirect to login with return path
    return {
      name: "login",
      query: { redirect: to.fullPath },
    };
  }
  
  if (guestOnly && isAuthenticated) {
    // Redirect authenticated users away from guest pages
    return { name: "dashboard" };
  }
  
  // Allow navigation
  return true;
});

export default router;
