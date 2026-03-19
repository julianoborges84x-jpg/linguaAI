import { expect, test } from "@playwright/test";

async function registerUser(request, email, password = "123") {
  const register = await request.post("http://127.0.0.1:8000/users", {
    data: { name: "E2E User", email, password },
  });
  expect(register.ok()).toBeTruthy();
}

test("usuário novo sem idioma vê onboarding e escolhe idioma em 1 clique", async ({ page, request }) => {
  const stamp = Date.now();
  const email = `onboarding-${stamp}@example.com`;
  const password = "123";

  await registerUser(request, email, password);

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Senha").fill(password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/onboarding$/, { timeout: 15000 });

  await expect(page.getByText("Qual idioma você quer aprender?")).toBeVisible();
  await page.getByRole("button", { name: "Inglês" }).click();
  await page.getByRole("button", { name: "Continuar" }).click();
  await page.getByRole("button", { name: "Começar" }).click();
  await expect(page.getByText("Seu painel")).toBeVisible({ timeout: 15000 });
});

test("após salvar idioma onboarding não aparece mais", async ({ page, request }) => {
  const stamp = Date.now();
  const email = `onboarding-done-${stamp}@example.com`;
  const password = "123";

  await registerUser(request, email, password);

  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Senha").fill(password);
  await page.getByRole("button", { name: "Entrar" }).click();
  await expect(page).toHaveURL(/\/onboarding$/, { timeout: 15000 });

  await page.getByRole("button", { name: "Espanhol" }).click();
  await page.getByRole("button", { name: "Continuar" }).click();
  await page.getByRole("button", { name: "Começar" }).click();
  await expect(page.getByText("Seu painel")).toBeVisible({ timeout: 15000 });

  await page.reload();
  await expect(page.getByText("Seu painel")).toBeVisible();
  await expect(page.getByText("Qual idioma você quer aprender?")).not.toBeVisible();
});
