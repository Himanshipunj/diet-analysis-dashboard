"use client";

import { useContext, createContext, useState, useEffect } from "react";
import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut,
    onAuthStateChanged,
    signInWithPopup,
    GithubAuthProvider,
    User,
    updateProfile,
} from "firebase/auth";
import { auth } from "./firebase";

interface AuthContextType {
    user: User | null;
    loading: boolean;
    emailSignIn: (email: string, password: string) => Promise<void>;
    emailSignUp: (email: string, password: string, displayName: string) => Promise<void>;
    gitHubSignIn: () => Promise<void>;
    firebaseSignOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    loading: true,
    emailSignIn: async () => { },
    emailSignUp: async () => { },
    gitHubSignIn: async () => { },
    firebaseSignOut: async () => { },
});

export const AuthContextProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    const emailSignIn = async (email: string, password: string) => {
        try {
            await signInWithEmailAndPassword(auth, email, password);
        } catch (error: any) {
            throw new Error(error.message);
        }
    };

    const emailSignUp = async (email: string, password: string, displayName: string) => {
        try {
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            // Update user profile with display name
            if (userCredential.user) {
                await updateProfile(userCredential.user, {
                    displayName: displayName,
                });
                // Force refresh to update the user object with the new display name
                setUser({ ...userCredential.user, displayName } as User);
            }
        } catch (error: any) {
            throw new Error(error.message);
        }
    };

    const gitHubSignIn = async () => {
        try {
            const provider = new GithubAuthProvider();
            await signInWithPopup(auth, provider);
        } catch (error: any) {
            throw new Error(error.message);
        }
    };

    const firebaseSignOut = async () => {
        try {
            await signOut(auth);
        } catch (error: any) {
            throw new Error(error.message);
        }
    };

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
            setUser(currentUser);
            setLoading(false);
        });
        return () => unsubscribe();
    }, []);

    return (
        <AuthContext.Provider value={{ user, loading, emailSignIn, emailSignUp, gitHubSignIn, firebaseSignOut }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useUserAuth = () => {
    return useContext(AuthContext);
};
