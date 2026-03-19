import { expect, test } from "@playwright/test";

const API_URL = "http://127.0.0.1:8000";

async function registerViaApi(request, email, password = "123", name = "E2E User") {
  const register = await request.post(`${API_URL}/users`, {
    data: { name, email, password },
  });
  expect(register.ok()).toBeTruthy();
  return register.json();
}

async function loginViaApi(request, email, password = "123") {
  const login = await request.post(`${API_URL}/auth/login`, {
    form: { username: email, password },
  });
  expect(login.ok()).toBeTruthy();
  const body = await login.json();
  return body.access_token;
}

async function setTargetLanguage(request, token, languageCode = "en") {
  const response = await request.patch(`${API_URL}/users/me`, {
    headers: { Authorization: `Bearer ${token}` },
    data: { target_language: languageCode, timezone: "America/Sao_Paulo" },
  });
  expect(response.ok()).toBeTruthy();
}

async function setUserLevel(request, userId, targetLevel) {
  const response = await request.patch(`${API_URL}/users/${userId}`, {
    data: { level: targetLevel },
  });
  expect(response.ok()).toBeTruthy();
}

async function registerAndLoginViaUi(page, email, password = "123") {
  await page.goto("/register");
  await page.getByLabel("Nome").fill("Usuário E2E");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Senha").fill(password);
  await page.getByRole("button", { name: "Criar conta" }).click();
  await expect(page).toHaveURL(/\/login$/, { timeout: 15000 });

  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Senha").fill(password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/onboarding$/, { timeout: 15000 });
}

test("cadastro e login de iniciante exibem onboarding", async ({ page }) => {
  const stamp = Date.now();
  const email = `beginner-${stamp}@example.com`;

  await registerAndLoginViaUi(page, email);
  await expect(page.getByText("Qual idioma você quer aprender?")).toBeVisible();
});

test("cada nivel de conhecimento aparece no dashboard", async ({ page, request }) => {
  const stamp = Date.now();
  const scenarios = [
    { level: 0, suffix: "lvl0" },
    { level: 1, suffix: "lvl1" },
    { level: 3, suffix: "lvl3" },
  ];

  for (const scenario of scenarios) {
    const email = `${scenario.suffix}-${stamp}@example.com`;
    const password = "123";
    const user = await registerViaApi(request, email, password);
    const token = await loginViaApi(request, email, password);
    await setTargetLanguage(request, token, "en");
    if (scenario.level > 0) {
      await setUserLevel(request, user.id, scenario.level);
    }

    await page.goto("/login");
    await page.getByLabel("Email").fill(email);
    await page.getByLabel("Senha").fill(password);
    await page.getByRole("button", { name: "Entrar" }).click();
    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 15000 });
    await expect(page.getByText(`Nível ${scenario.level}`)).toBeVisible({ timeout: 15_000 });
  }
});

test("conta PRO aparece corretamente no frontend real", async ({ page, request }) => {
  const stamp = Date.now();
  const email = `pro-${stamp}@example.com`;
  const password = "123";

  const user = await registerViaApi(request, email, password, "Usuário PRO");
  const setPro = await request.patch(`${API_URL}/users/${user.id}`, {
    data: { plan: "PRO", target_language: "en" },
  });
  expect(setPro.ok()).toBeTruthy();

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Senha").fill(password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/dashboard$/, { timeout: 15000 });
  await expect(page.getByText("Plano PRO")).toBeVisible({ timeout: 15_000 });
});

test("botão Assinar PRO dispara checkout e redireciona", async ({ page, request }) => {
  const stamp = Date.now();
  const email = `checkout-${stamp}@example.com`;
  const password = "123";

  await registerViaApi(request, email, password, "Usuário Checkout");
  const token = await loginViaApi(request, email, password);
  await setTargetLanguage(request, token, "en");

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Senha").fill(password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/dashboard$/, { timeout: 15000 });

  const checkoutReq = page.waitForRequest((req) => {
    return req.method() === "POST" && req.url().includes("/billing/create-checkout-session");
  });
  await page.getByRole("button", { name: "Assinar PRO" }).click();
  await checkoutReq;
  await expect(page).toHaveURL(/\/billing\/fake-checkout\?user_id=/, { timeout: 15000 });
});
