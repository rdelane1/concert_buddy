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

async function backendFetch(url: string): Promise<Response> {
  if (isLocalBackend(getBackendUrl())) {
    return fetch(url, {
      headers: {
        Accept: "text/event-stream",
      },
      cache: "no-store",
    });
  }

  const auth = new GoogleAuth();
  const client = await auth.getIdTokenClient(getBackendUrl());
  const authHeaders = await client.getRequestHeaders(url);

  return fetch(url, {
    headers: {
      ...authHeaders,
      Accept: "text/event-stream",
    },
  });
}

export async function GET(request: NextRequest) {
  try {
    const sessionId = request.nextUrl.searchParams.get("session_id");

    if (!sessionId) {
      return NextResponse.json(
        { error: "session_id is required" },
        { status: 400 }
      );
    }

    const response = await backendFetch(
      `${getBackendUrl()}/events?session_id=${encodeURIComponent(sessionId)}`
    );

    if (!response.body) {
      return NextResponse.json(
        { error: "Backend event stream unavailable" },
        { status: 502 }
      );
    }

    return new NextResponse(response.body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("content-type") ?? "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    console.error("Events proxy error:", error);

    return NextResponse.json(
      { error: "Failed to reach backend event service." },
      { status: 500 }
    );
  }
}
