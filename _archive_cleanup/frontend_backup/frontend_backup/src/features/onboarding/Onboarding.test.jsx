import React from "react";
import { MemoryRouter } from "react-router-dom";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import Onboarding from "./Onboarding.jsx";

const setUserMock = vi.fn();
const navigateMock = vi.fn();
const completeOnboardingMock = vi.fn();
const getCurrentUserMock = vi.fn();

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => navigateMock,
  };
});

vi.mock("../../hooks/useAuth.jsx", () => ({
  useAuth: () => ({ setUser: setUserMock }),
}));

vi.mock("../../services/userService.js", () => ({
  completeOnboarding: (...args) => completeOnboardingMock(...args),
  getCurrentUser: (...args) => getCurrentUserMock(...args),
}));

function renderOnboarding() {
  return render(
    <MemoryRouter>
      <Onboarding />
    </MemoryRouter>
  );
}

describe("Onboarding page", () => {
  afterEach(() => {
    cleanup();
  });

  beforeEach(() => {
    vi.clearAllMocks();
    getCurrentUserMock.mockResolvedValue({
      id: 1,
      name: "User",
      onboarding_completed: true,
      target_language: "en",
      timezone: "America/Sao_Paulo",
    });
  });

  it("renderiza a tela de onboarding", () => {
    renderOnboarding();
    expect(screen.getByText("Primeira configuração")).toBeInTheDocument();
    expect(screen.getByText("Só 2 passos e você começa.")).toBeInTheDocument();
  });

  it("seleciona idioma e avança para passo 2", async () => {
    renderOnboarding();
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: "Inglês" }));
    await user.click(screen.getByRole("button", { name: "Continuar" }));

    expect(screen.getByText("Seu fuso horário")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Começar" })).toBeInTheDocument();
  });

  it("submete e chama PATCH /users/me", async () => {
    completeOnboardingMock.mockResolvedValue({
      onboarding_completed: true,
      target_language: "en",
      timezone: "America/Sao_Paulo",
    });

    renderOnboarding();
    const user = userEvent.setup();

    await user.click(screen.getByRole("button", { name: "Inglês" }));
    await user.click(screen.getByRole("button", { name: "Continuar" }));
    await user.selectOptions(screen.getByRole("combobox"), "America/Sao_Paulo");
    await user.click(screen.getByRole("button", { name: "Começar" }));

    await waitFor(() => {
      expect(completeOnboardingMock).toHaveBeenCalledWith({
        target_language: "en",
        timezone: "America/Sao_Paulo",
      });
    });
    await waitFor(() => {
      expect(navigateMock).toHaveBeenCalledWith("/dashboard", { replace: true });
    });
  });
});
