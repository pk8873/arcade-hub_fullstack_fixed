import {
  createRootRoute, createRoute, createRouter, Outlet, Link, redirect,
} from "@tanstack/react-router";
import { RootLayout } from "./routes/__root";
import { HomePage } from "./routes/index";
import { LoginPage } from "./routes/login";
import { SignupPage } from "./routes/signup";
import { VerifyPage } from "./routes/verify";
import { VerifiedPage } from "./routes/verified";
import { ForgotPasswordPage } from "./routes/forgot-password";
import { ResetPasswordPage } from "./routes/reset-password";
import { DashboardPage } from "./routes/dashboard";
import { WalletPage } from "./routes/wallet";
import { GamesPage } from "./routes/games";
import { SkyClimbPage } from "./routes/skyclimb";
import { FlashDuelPage } from "./routes/flashduel";
import { StocksPage } from "./routes/stocks";
import { AdminPage } from "./routes/admin";
import { getToken } from "./lib/api";

const rootRoute = createRootRoute({ component: RootLayout });

const indexRoute = createRoute({ getParentRoute: () => rootRoute, path: "/", component: HomePage });
const loginRoute = createRoute({ getParentRoute: () => rootRoute, path: "/login", component: LoginPage });
const signupRoute = createRoute({ getParentRoute: () => rootRoute, path: "/signup", component: SignupPage });
const verifyRoute = createRoute({ getParentRoute: () => rootRoute, path: "/verify", component: VerifyPage });
const verifiedRoute = createRoute({ getParentRoute: () => rootRoute, path: "/verified", component: VerifiedPage });
const forgotPasswordRoute = createRoute({ getParentRoute: () => rootRoute, path: "/forgot-password", component: ForgotPasswordPage });
const resetPasswordRoute = createRoute({ getParentRoute: () => rootRoute, path: "/reset-password", component: ResetPasswordPage });

function requireAuth() {
  if (!getToken()) throw redirect({ to: "/login" });
}

const dashboardRoute = createRoute({ getParentRoute: () => rootRoute, path: "/dashboard", beforeLoad: requireAuth, component: DashboardPage });
const walletRoute = createRoute({ getParentRoute: () => rootRoute, path: "/wallet", beforeLoad: requireAuth, component: WalletPage });
const gamesRoute = createRoute({ getParentRoute: () => rootRoute, path: "/games", beforeLoad: requireAuth, component: GamesPage });
const skyRoute = createRoute({ getParentRoute: () => rootRoute, path: "/games/skyclimb", beforeLoad: requireAuth, component: SkyClimbPage });
const flashRoute = createRoute({ getParentRoute: () => rootRoute, path: "/games/flashduel", beforeLoad: requireAuth, component: FlashDuelPage });
const stocksRoute = createRoute({ getParentRoute: () => rootRoute, path: "/games/stocks", beforeLoad: requireAuth, component: StocksPage });
const adminRoute = createRoute({ getParentRoute: () => rootRoute, path: "/admin", beforeLoad: requireAuth, component: AdminPage });

const routeTree = rootRoute.addChildren([
  indexRoute, loginRoute, signupRoute, verifyRoute, verifiedRoute,
  forgotPasswordRoute, resetPasswordRoute,
  dashboardRoute, walletRoute, gamesRoute, skyRoute, flashRoute, stocksRoute, adminRoute,
]);

export const router = createRouter({ routeTree, defaultPreload: "intent" });

declare module "@tanstack/react-router" {
  interface Register { router: typeof router; }
}

export { Link, Outlet };
