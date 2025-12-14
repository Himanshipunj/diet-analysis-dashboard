"use client";

import { useUserAuth } from "../utils/auth-context";

interface UserHeaderProps {
    userName: string | null;
}

export default function UserHeader({ userName }: UserHeaderProps) {
    const { firebaseSignOut } = useUserAuth();

    const handleLogout = async () => {
        try {
            await firebaseSignOut();
        } catch (error) {
            console.error("Logout error:", error);
        }
    };

    return (
        <div className="bg-white shadow-sm border-b border-gray-200 px-6 py-3">
            <div className="max-w-7xl mx-auto flex justify-between items-center">
                <div className="flex items-center">
                    <h2 className="text-xl font-semibold text-gray-800">
                        🍎 Nutritional Insights Dashboard
                    </h2>
                </div>
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                            <span className="text-white font-semibold text-sm">
                                {userName ? userName.charAt(0).toUpperCase() : "U"}
                            </span>
                        </div>
                        <span className="text-gray-700 font-medium">
                            {userName || "User"}
                        </span>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition duration-200"
                    >
                        Logout
                    </button>
                </div>
            </div>
        </div>
    );
}
