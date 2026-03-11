import { beforeEach, describe, expect, it, vi } from "vitest";

const storageGet = vi.fn();
const storageRemove = vi.fn();

vi.mock("../storage.js", () => ({
  default: {
    get: (...args) => storageGet(...args),
    remove: (...args) => storageRemove(...args),
  },
}));

describe("apiClient", () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
    global.fetch = vi.fn();
    global.window = { location: { pathname: "/dashboard", href: "" } };
  });

  it("envia Authorization quando existe token", async () => {
    storageGet.mockReturnValue("token-123");
    fetch.mockResolvedValue({
      ok: true,
      text: async () => JSON.stringify({ ok: true }),
    });

    const { request } = await import("../apiClient.js");
    await request("/users/me", { method: "GET" });

    const [, options] = fetch.mock.calls[0];
    expect(options.headers.Authorization).toBe("Bearer token-123");
  });

  it("mantem content-type customizado para oauth2 form", async () => {
    storageGet.mockReturnValue(null);
    fetch.mockResolvedValue({
      ok: true,
      text: async () => JSON.stringify({ access_token: "x" }),
    });

    const { request } = await import("../apiClient.js");
    await request("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ username: "u", password: "p" }),
    });

    const [, options] = fetch.mock.calls[0];
    expect(options.headers["Content-Type"]).toBe("application/x-www-form-urlencoded");
  });

  it("em 401 limpa token e redireciona para /login", async () => {
    storageGet.mockReturnValue("token-401");
    fetch.mockResolvedValue({
      ok: false,
      status: 401,
      text: async () => JSON.stringify({ detail: "Invalid token" }),
    });

    const { request } = await import("../apiClient.js");
    await expect(request("/users/me", { method: "GET" })).rejects.toThrow("Invalid token");
    expect(storageRemove).toHaveBeenCalledWith("auth_token");
    expect(window.location.href).toBe("/login");
  });

  it("em 401 não redireciona quando redirectOnAuthError=false", async () => {
    storageGet.mockReturnValue("token-401");
    fetch.mockResolvedValue({
      ok: false,
      status: 401,
      text: async () => JSON.stringify({ detail: "Invalid token" }),
    });

    const { request } = await import("../apiClient.js");
    await expect(
      request("/billing/create-checkout-session", {
        method: "POST",
        redirectOnAuthError: false,
      })
    ).rejects.toThrow("Invalid token");
    expect(storageRemove).toHaveBeenCalledWith("auth_token");
    expect(window.location.href).toBe("");
  });
});
