import { clerkMiddleware, createRouteMatcher } from "@clerk/astro/server";

// Define routes that don't require authentication (e.g., your custom login page)
const isPublicRoute = createRouteMatcher(['/login']);

export const onRequest = clerkMiddleware((auth, context) => {
  const { userId } = auth();

  // If the user is NOT logged in and the route is NOT public, redirect to /login
  if (!userId && !isPublicRoute(context.request)) {
    return context.redirect('/login');
  }
});