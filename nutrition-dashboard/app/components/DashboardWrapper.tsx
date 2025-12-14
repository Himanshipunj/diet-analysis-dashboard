"use client";

import { useUserAuth } from "../utils/auth-context";
import AuthForm from "./AuthForm";
import UserHeader from "./UserHeader";

interface DashboardWrapperProps {
    children: React.ReactNode;
}

export default function DashboardWrapper({ children }: DashboardWrapperProps) {
    const { user, loading, emailSignIn, emailSignUp, gitHubSignIn } = useUserAuth();

    // Show loading spinner while checking authentication state
    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-100">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    <p className="mt-4 text-gray-600">Loading...</p>
                </div>
            </div>
        );
    }

    // If user is not authenticated, show login/register form
    if (!user) {
        return <AuthForm onSignIn={emailSignIn} onSignUp={emailSignUp} onGitHubSignIn={gitHubSignIn} />;
    }

    // If user is authenticated, show dashboard with user header
    return (
        <div className="min-h-screen">
            <UserHeader userName={user.displayName || user.email} />
            {children}
        </div>
    );
}
