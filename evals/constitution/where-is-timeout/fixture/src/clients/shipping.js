import { request } from './http.js';

export async function quote(address, weightGrams) {
  const response = await request('http://shipping.internal/quote', {
    method: 'POST',
    body: JSON.stringify({ address, weightGrams }),
  });
  return response.json();
}
