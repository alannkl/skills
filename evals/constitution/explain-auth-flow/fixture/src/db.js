const users = [{ id: 1, email: 'ana@studio.example', role: 'admin', passwordHash: '$2b$12$abcdefghijklmnopqrstuuv0n7Tq3o2gC7sYkq3F5qkzR6m1mO9e' }];
const projects = [{ id: 1, ownerId: 1, name: 'Rebrand' }];

export async function findUserByEmail(email) {
  return users.find((u) => u.email === email);
}

export async function listProjects(userId) {
  return projects.filter((p) => p.ownerId === userId);
}

export async function deleteProject(id) {
  const index = projects.findIndex((p) => p.id === Number(id));
  if (index !== -1) projects.splice(index, 1);
}
