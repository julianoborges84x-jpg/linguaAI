export async function startProCheckout({
  subscribe = null,
  redirect = null,
} = {}) {
  const subscribeFn = subscribe || (() => Promise.reject(new Error("subscribe function is required")));
  const redirectFn = redirect || ((url) => window.location.assign(url));

  const data = await subscribeFn();
  const checkout_url = data?.checkout_url || data?.url || null;
  if (!checkout_url) {
    throw new Error("Checkout indisponível no momento.");
  }

  redirectFn(checkout_url);
  return { checkout_url };
}
