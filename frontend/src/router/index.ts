import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { useAuthStore } from "@/stores/auth";

declare module "vue-router" {
  interface RouteMeta {
    requiresAuth?: boolean;
    guestOnly?: boolean;
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
    path: "/verify-email",
    name: "verifyEmail",
    component: () => import("@/views/VerifyEmailView.vue"),
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
        path: "settings",
        name: "settings",
        component: () => import("@/views/SettingsView.vue"),
      },
      {
        path: "recipients",
        name: "recipients",
        component: () => import("@/views/RecipientsView.vue"),
      },
      {
        path: "recipients/:recipient_id",
        name: "recipientDetails",
        component: () => import("@/views/RecipientDetailsView.vue"),
      },
      {
        path: "gifts",
        name: "gifts",
        component: () => import("@/views/GiftsView.vue"),
      },
      {
        path: "gifts/:gift_id",
        name: "giftDetails",
        component: () => import("@/views/GiftDetailsView.vue"),
      },
      {
        path: "budget",
        name: "budget",
        component: () => import("@/views/BudgetView.vue"),
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
  console.log("Start of the beforeEach router.");
  
  const authStore = useAuthStore();
  
  // Initialize auth state on first navigation
  if (!authStore.isInitialized && !authStore.isInitializing) {
    console.log("authStore.initialize(): start");
    await authStore.initialize();
    console.log("authStore.initialize(): end");
  }

  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const guestOnly = to.matched.some((record) => record.meta.guestOnly);
  const isAuthenticated = authStore.isAuthenticated;
  console.log("isAuthenticated:", isAuthenticated, "and requiresAuth:", requiresAuth, "and guestOnly:", guestOnly);

  if (requiresAuth && !isAuthenticated) {
    // Redirect to login with return path
    console.log("Redirecting to login with return path");
    return {
      name: "login",
      query: { redirect: to.fullPath },
    };
  }
  
  if (guestOnly && isAuthenticated) {
    // Redirect authenticated users away from guest pages
    console.log("Redirecting authenticated users away from guest pages");
    
    return { name: "dashboard" };
  }

  // Allow navigation
  console.log('allowing navigation');
  return true;
});

export default router;
