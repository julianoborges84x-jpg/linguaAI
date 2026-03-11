import { describe, expect, it, vi } from "vitest";
import { startProCheckout } from "./checkoutFlow.js";

describe("startProCheckout", () => {
  it("chama subscribe e redireciona com checkout_url", async () => {
    const subscribe = vi.fn().mockResolvedValue({
      checkout_url: "https://checkout.stripe.test/session_123",
    });
    const redirect = vi.fn();

    const result = await startProCheckout({ subscribe, redirect });

    expect(subscribe).toHaveBeenCalledTimes(1);
    expect(redirect).toHaveBeenCalledWith("https://checkout.stripe.test/session_123");
    expect(result).toEqual({ checkout_url: "https://checkout.stripe.test/session_123" });
  });

  it("lança erro quando checkout_url não vem na resposta", async () => {
    const subscribe = vi.fn().mockResolvedValue({ ok: true });
    const redirect = vi.fn();

    await expect(startProCheckout({ subscribe, redirect })).rejects.toThrow(
      "Checkout indisponível no momento."
    );
    expect(redirect).not.toHaveBeenCalled();
  });
});
