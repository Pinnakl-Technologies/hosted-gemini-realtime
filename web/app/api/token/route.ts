import { AccessToken } from 'livekit-server-sdk';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
    const roomName = 'rehmat-call-' + Math.random().toString(36).substring(7);
    const participantName = 'customer-' + Math.random().toString(36).substring(7);

    const apiKey = process.env.LIVEKIT_API_KEY!;
    const apiSecret = process.env.LIVEKIT_API_SECRET!;
    const wsUrl = process.env.LIVEKIT_URL!;

    if (!apiKey || !apiSecret || !wsUrl) {
        return NextResponse.json(
            { error: 'Server misconfigured' },
            { status: 500 }
        );
    }

    const at = new AccessToken(apiKey, apiSecret, {
        identity: participantName,
        name: participantName,
    });

    at.addGrant({
        room: roomName,
        roomJoin: true,
        canPublish: true,
        canSubscribe: true,
    });

    return NextResponse.json({
        token: await at.toJwt(),
        url: wsUrl,
        roomName,
    });
}
