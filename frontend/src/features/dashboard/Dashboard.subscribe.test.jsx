import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Dashboard from "./Dashboard.jsx";

const mockSetUser = vi.fn();
const mockLogout = vi.fn();

vi.mock("../../hooks/useAuth.jsx", () => ({
  useAuth: () => ({
    user: {
      id: 1,
      name: "Teste",
      plan: "FREE",
      level: 1,
      timezone: "America/Sao_Paulo",
      onboarding_completed: true,
      target_language_code: "en",
    },
    setUser: mockSetUser,
    logout: mockLogout,
  }),
}));

const subscribeProMock = vi.fn();

vi.mock("../../services/billingService.js", () => ({
  getBillingStatus: vi.fn().mockResolvedValue({ stripe_configured: true, plan: "FREE" }),
  subscribePro: (...args) => subscribeProMock(...args),
  cancelSubscription: vi.fn(),
  openCustomerPortal: vi.fn(),
}));

vi.mock("../../services/userService.js", () => ({
  getCurrentUser: vi.fn().mockResolvedValue({
    id: 1,
    name: "Teste",
    plan: "FREE",
    level: 1,
    timezone: "America/Sao_Paulo",
    onboarding_completed: true,
    target_language_code: "en",
  }),
}));

vi.mock("../../services/dailyMessageService.js", () => ({
  getDailyMessage: vi.fn().mockResolvedValue({ message: "msg" }),
  getStreak: vi.fn().mockResolvedValue({ streak: 1 }),
}));

vi.mock("../../services/mentorService.js", () => ({
  getMentorHistory: vi.fn().mockResolvedValue([]),
  getWeeklyProgress: vi.fn().mockResolvedValue([]),
}));

vi.mock("../../services/learnaService.js", () => ({
  getProgressSummary: vi.fn().mockResolvedValue({ xp_total: 0, level: 1, streak_days: 1, weekly_minutes: 0 }),
}));

vi.mock("../../shared/layouts/PageShell.jsx", () => ({
  default: ({ children }) => <div>{children}</div>,
}));
vi.mock("../../shared/components/NavBar.jsx", () => ({
  default: () => <div>nav</div>,
}));
vi.mock("../../shared/components/DailyMessage.jsx", () => ({
  default: () => <div>daily</div>,
}));
vi.mock("../../shared/components/AdsPanel.jsx", () => ({
  default: () => <div>ads</div>,
}));
vi.mock("../../shared/components/ProgressChart.jsx", () => ({
  default: () => <div>chart</div>,
}));
vi.mock("../../shared/components/HistoryList.jsx", () => ({
  default: () => <div>history</div>,
}));
vi.mock("../../shared/components/StreakBadge.jsx", () => ({
  default: () => <div>streak</div>,
}));
vi.mock("../../shared/ui/Card.jsx", () => ({
  default: ({ children }) => <div>{children}</div>,
}));

describe("Dashboard subscribe", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    subscribeProMock.mockResolvedValue({
      checkout_url: "http://localhost:5173/billing/fake-checkout?user_id=1",
    });
    Object.defineProperty(window, "location", {
      configurable: true,
      value: {
        assign: vi.fn(),
        href: "",
        pathname: "/dashboard",
      },
    });
  });

  it("clica em Assinar PRO e redireciona para checkout", async () => {
    render(<Dashboard />);
    const button = await screen.findByRole("button", { name: "Assinar PRO" });
    await userEvent.click(button);

    await waitFor(() => {
      expect(subscribeProMock).toHaveBeenCalledTimes(1);
    });
    expect(window.location.assign).toHaveBeenCalledWith(
      "http://localhost:5173/billing/fake-checkout?user_id=1"
    );
  });
});
