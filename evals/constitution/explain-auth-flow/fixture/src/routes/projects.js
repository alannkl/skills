import { Router } from 'express';
import { requireUser, requireRole } from '../middleware/requireUser.js';
import { listProjects, deleteProject } from '../db.js';

const router = Router();

router.use(requireUser);
router.get('/', async (req, res) => res.json(await listProjects(req.session.userId)));
router.delete('/:id', requireRole('admin'), async (req, res) => {
  await deleteProject(req.params.id);
  res.status(204).end();
});

export default router;
