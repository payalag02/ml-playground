const { Router } = require("express");
const ctrl = require("../controllers/metrics.controller");

const router = Router();

router.post("/track", ctrl.track);
router.get("/realtime", ctrl.realtime);
router.get("/persisted", ctrl.persisted);
router.get("/history/:event", ctrl.history);

module.exports = router;
