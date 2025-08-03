import { NextRequest } from 'next/server';

// Simple in-memory rate limiting for development
// In production, use Redis or a proper rate limiting service
const requests = new Map<string, { count: number; resetTime: number }>();

export interface RateLimitResult {
  success: boolean;
  remaining: number;
  resetTime: number;
}

export async function rateLimit(request: NextRequest): Promise<RateLimitResult> {
  const forwarded = request.headers.get('x-forwarded-for');
  const ip = forwarded ? forwarded.split(',')[0] : 'anonymous';
  const now = Date.now();
  const windowMs = parseInt(process.env.RATE_LIMIT_WINDOW || '60000'); // 1 minute
  const maxRequests = parseInt(process.env.RATE_LIMIT_MAX || '30');
  
  const key = `rate_limit:${ip}`;
  const current = requests.get(key);
  
  if (!current || now > current.resetTime) {
    // Reset window
    requests.set(key, {
      count: 1,
      resetTime: now + windowMs,
    });
    
    return {
      success: true,
      remaining: maxRequests - 1,
      resetTime: now + windowMs,
    };
  }
  
  if (current.count >= maxRequests) {
    return {
      success: false,
      remaining: 0,
      resetTime: current.resetTime,
    };
  }
  
  current.count++;
  requests.set(key, current);
  
  return {
    success: true,
    remaining: maxRequests - current.count,
    resetTime: current.resetTime,
  };
}

// Cleanup old entries periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, value] of requests.entries()) {
    if (now > value.resetTime) {
      requests.delete(key);
    }
  }
}, 60000); // Clean up every minute