import { GoogleAuth } from "google-auth-library";
import { NextRequest, NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND_URL = process.env.BACKEND_URL;

function getBackendUrl(): string {
  if (!BACKEND_URL) {
    throw new Error("BACKEND_URL is not configured");
  }

  return BACKEND_URL.replace(/\/$/, "");
}

function isLocalBackend(url: string): boolean {
  return /^https?:\/\/(localhost|127\.0\.0\.1|backend)(:\d+)?$/i.test(url);
}

async function backendFetch(url: string, init?: RequestInit): Promise<Response> {
  if (isLocalBackend(getBackendUrl())) {
    return fetch(url, init);
  }

  const auth = new GoogleAuth();
  const client = await auth.getIdTokenClient(getBackendUrl());
  const authHeaders = await client.getRequestHeaders(url);

  return fetch(url, {
    method: init?.method,
    headers: {
      ...authHeaders,
      ...(init?.headers ?? {}),
    },
    body: init?.body,
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.text();
    const response = await backendFetch(`${getBackendUrl()}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body,
    });

    const text = await response.text();

    return new NextResponse(text, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("content-type") ?? "application/json",
      },
    });
  } catch (error) {
    console.error("Chat proxy error:", error);

    return NextResponse.json(
      { error: "Failed to reach backend chat service." },
      { status: 500 }
    );
  }
}
