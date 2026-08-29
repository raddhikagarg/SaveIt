"use client";

import { useCallback, useEffect, useRef } from "react";
import Script from "next/script";
import { useAuth } from "@/lib/auth-context";

declare global {
    interface Window {
        google?: any;
    }
}

export default function GoogleSignInButton() {
    const buttonRef = useRef<HTMLDivElement>(null);
    const initializedRef = useRef(false);
    const { login } = useAuth();

    const handleCredentialResponse = useCallback(
        async (response: { credential: string }) => {
            console.log("Google credential received:", !!response.credential);
            console.log("Credential length:", response.credential?.length);

            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL;

                if (!apiUrl) {
                    throw new Error("NEXT_PUBLIC_API_URL is not configured");
                }

                console.log("Calling backend:", `${apiUrl}/auth/google`);

                const res = await fetch(`${apiUrl}/auth/google`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        id_token: response.credential,
                    }),
                });

                if (!res.ok) {
                    const errorText = await res.text();
                    console.error("Backend response:", res.status, errorText);
                    throw new Error(`Login failed: ${res.status}`);
                }

                const data = await res.json();
                login(data.access_token, data.user);
            } catch (err) {
                console.error("Google login error:", err);
            }
        },
        [login]
    );

    const initializeGoogle = useCallback(() => {
        if (
            !window.google ||
            !buttonRef.current ||
            initializedRef.current
        ) {
            return;
        }

        const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

        // DEBUG: confirms which client ID the frontend is using
        console.log(
            "Client ID:",
            clientId ? `${clientId.slice(0, 12)}...` : "undefined"
        );

        if (!clientId) {
            console.error("NEXT_PUBLIC_GOOGLE_CLIENT_ID is missing");
            return;
        }

        initializedRef.current = true;

        window.google.accounts.id.initialize({
            client_id: clientId,
            callback: handleCredentialResponse,
        });

        window.google.accounts.id.renderButton(buttonRef.current, {
            theme: "outline",
            size: "large",
        });
    }, [handleCredentialResponse]);

    useEffect(() => {
        initializeGoogle();
    }, [initializeGoogle]);

    return (
        <>
            <Script
                src="https://accounts.google.com/gsi/client"
                strategy="afterInteractive"
                onLoad={initializeGoogle}
            />
            <div ref={buttonRef} />
        </>
    );
}