import { beforeEach, describe, expect, it, vi } from "vitest";

const requestMock = vi.fn();
const storageMock = {
  get: vi.fn(),
  set: vi.fn(),
  remove: vi.fn(),
};

vi.mock("../../core/apiClient.js", () => ({
  default: { request: (...args) => requestMock(...args) },
}));

vi.mock("../../core/storage.js", () => ({
  default: storageMock,
}));

describe("authService", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("login usa oauth2 form e salva token", async () => {
    requestMock.mockResolvedValue({ access_token: "jwt-1", token_type: "bearer" });
    const { login, getToken } = await import("../authService.js");

    await login("ana@example.com", "123");
    expect(requestMock).toHaveBeenCalledTimes(1);
    const [path, options] = requestMock.mock.calls[0];
    expect(path).toBe("/auth/login");
    expect(options.method).toBe("POST");
    expect(options.headers["Content-Type"]).toBe("application/x-www-form-urlencoded");
    expect(options.body.get("username")).toBe("ana@example.com");
    expect(options.body.get("password")).toBe("123");
    expect(storageMock.set).toHaveBeenCalledWith("auth_token", "jwt-1");

    storageMock.get.mockReturnValue("jwt-1");
    expect(getToken()).toBe("jwt-1");
  });

  it("register envia payload correto", async () => {
    requestMock.mockResolvedValue({ id: 1 });
    const { register } = await import("../authService.js");

    await register({ name: "Ana", email: "ana@example.com", password: "abc" });
    const [path, options] = requestMock.mock.calls[0];
    expect(path).toBe("/users");
    expect(options.method).toBe("POST");
    expect(JSON.parse(options.body)).toEqual({
      name: "Ana",
      email: "ana@example.com",
      password: "abc",
    });
  });
});

describe("user/mentor/billing services", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("updateUser usa PATCH /users/me", async () => {
    requestMock.mockResolvedValue({ id: 1 });
    const { updateUser } = await import("../userService.js");

    const payload = {
      target_language_code: "eng",
      base_language_code: "por",
      timezone: "America/Sao_Paulo",
      plan: "FREE",
      level: 0,
    };
    await updateUser(payload);

    const [path, options] = requestMock.mock.calls[0];
    expect(path).toBe("/users/me");
    expect(options.method).toBe("PATCH");
    expect(JSON.parse(options.body)).toEqual(payload);
  });

  it("preferences usam endpoints corretos", async () => {
    requestMock.mockResolvedValue({ onboarding_completed: false });
    const { getUserPreferences, updateUserPreferences, completeOnboarding } = await import("../userService.js");

    await getUserPreferences();
    await updateUserPreferences({ target_language_code: "en", timezone: "America/Sao_Paulo" });
    await completeOnboarding({ target_language: "en", timezone: "America/Sao_Paulo" });

    expect(requestMock.mock.calls[0][0]).toBe("/users/preferences");
    expect(requestMock.mock.calls[0][1].method).toBe("GET");
    expect(requestMock.mock.calls[1][0]).toBe("/users/preferences");
    expect(requestMock.mock.calls[1][1].method).toBe("PUT");
    expect(JSON.parse(requestMock.mock.calls[1][1].body)).toEqual({
      target_language_code: "en",
      timezone: "America/Sao_Paulo",
    });
    expect(requestMock.mock.calls[2][0]).toBe("/users/me");
    expect(requestMock.mock.calls[2][1].method).toBe("PATCH");
    expect(JSON.parse(requestMock.mock.calls[2][1].body)).toEqual({
      target_language: "en",
      timezone: "America/Sao_Paulo",
    });
  });

  it("mentor chat/detect enviam campos esperados", async () => {
    requestMock.mockResolvedValue({});
    const { chatMentor, detectBaseLanguage } = await import("../mentorService.js");

    await detectBaseLanguage("ola");
    await chatMentor("texto", "writing");

    expect(requestMock.mock.calls[0][0]).toBe("/mentor/detect-language");
    expect(JSON.parse(requestMock.mock.calls[0][1].body)).toEqual({ text: "ola" });
    expect(requestMock.mock.calls[1][0]).toBe("/mentor/chat");
    expect(JSON.parse(requestMock.mock.calls[1][1].body)).toEqual({
      message: "texto",
      feature: "writing",
    });
  });

  it("billing usa endpoints corretos", async () => {
    requestMock.mockResolvedValue({});
    const { subscribePro, cancelSubscription, openCustomerPortal } = await import("../billingService.js");

    await subscribePro();
    await cancelSubscription();
    await openCustomerPortal();

    expect(requestMock.mock.calls[0][0]).toBe("/billing/create-checkout-session");
    expect(requestMock.mock.calls[1][0]).toBe("/billing/cancel-subscription");
    expect(requestMock.mock.calls[2][0]).toBe("/billing/create-portal-session");
  });

  it("subscribePro normaliza url legado para checkout_url", async () => {
    requestMock.mockResolvedValue({ url: "https://checkout.stripe.test/legacy" });
    const { subscribePro } = await import("../billingService.js");

    const response = await subscribePro();
    expect(response).toEqual({ checkout_url: "https://checkout.stripe.test/legacy" });
    expect(requestMock).toHaveBeenCalledWith("/billing/create-checkout-session", {
      method: "POST",
      redirectOnAuthError: false,
    });
  });

  it("subscribePro mantém checkout_url quando já vem padronizado", async () => {
    requestMock.mockResolvedValue({ checkout_url: "https://checkout.stripe.test/new" });
    const { subscribePro } = await import("../billingService.js");

    const response = await subscribePro();
    expect(response).toEqual({ checkout_url: "https://checkout.stripe.test/new" });
  });

  it("learna service usa endpoints corretos", async () => {
    requestMock.mockResolvedValue({});
    const {
      sendChatMessage,
      getTopics,
      getHistory,
      getVocabulary,
      getProgress,
      updateProgress,
      getProgressSummary,
      startStudySession,
      finishStudySession,
    } = await import("../learnaService.js");

    await sendChatMessage("hi");
    await getTopics();
    await getHistory();
    await getVocabulary();
    await getProgress();
    await updateProgress({ streak: 2 });
    await getProgressSummary();
    await startStudySession("chat", 2);
    await finishStudySession(10, 4);

    expect(requestMock.mock.calls[0][0]).toBe("/chat");
    expect(JSON.parse(requestMock.mock.calls[0][1].body)).toEqual({ message: "hi" });
    expect(requestMock.mock.calls[1][0]).toBe("/topics");
    expect(requestMock.mock.calls[2][0]).toBe("/history");
    expect(requestMock.mock.calls[3][0]).toBe("/vocabulary");
    expect(requestMock.mock.calls[4][0]).toBe("/progress");
    expect(requestMock.mock.calls[5][0]).toBe("/progress");
    expect(requestMock.mock.calls[5][1].method).toBe("PATCH");
    expect(requestMock.mock.calls[6][0]).toBe("/progress/summary");
    expect(requestMock.mock.calls[7][0]).toBe("/sessions/start");
    expect(JSON.parse(requestMock.mock.calls[7][1].body)).toEqual({ mode: "chat", topic_id: 2 });
    expect(requestMock.mock.calls[8][0]).toBe("/sessions/10/finish");
    expect(JSON.parse(requestMock.mock.calls[8][1].body)).toEqual({ interactions_count: 4 });
  });
});
