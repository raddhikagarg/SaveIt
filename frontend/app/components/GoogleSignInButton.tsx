"use client";

import { useEffect, useRef } from "react";
import Script from "next/script";
import { useAuth } from "@/lib/auth-context";

declare global {
    interface Window {
        google?: any;
    }
}

export default function GoogleSignInButton() {
    const buttonRef = useRef<HTMLDivElement>(null);
    const { login } = useAuth();

    const handleCredentialResponse = async (response: { credential: string }) => {
        try {
            const res = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/auth/google`,
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ id_token: response.credential }),
                }
            );
            if (!res.ok) throw new Error("Login failed");
            const data = await res.json();
            login(data.access_token, data.user);
        } catch (err) {
            console.error("Google login error:", err);
        }
    };

    useEffect(() => {
        if (window.google && buttonRef.current) {
            window.google.accounts.id.initialize({
                client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID,
                callback: handleCredentialResponse,
            });
            window.google.accounts.id.renderButton(buttonRef.current, {
                theme: "outline",
                size: "large",
            });
        }
    }, []);

    return (
        <>
            <Script src="https://accounts.google.com/gsi/client" strategy="afterInteractive" />
            <div ref={buttonRef}></div>
        </>
    );
}