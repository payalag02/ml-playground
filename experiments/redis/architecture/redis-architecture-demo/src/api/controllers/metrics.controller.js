const metricsService = require("../../domain/metrics.service");

const metricsController = {
  async track(req, res) {
    const { event, payload } = req.body;
    if (!event) return res.status(400).json({ error: "event is required" });
    await metricsService.trackEvent(event, payload);
    res.status(202).json({ status: "accepted" });
  },

  async realtime(req, res) {
    const counts = await metricsService.getRealtimeCounts();
    res.json(counts);
  },

  async persisted(req, res) {
    const counts = await metricsService.getPersistedCounts();
    res.json(counts);
  },

  async history(req, res) {
    const { event } = req.params;
    const data = await metricsService.getEventHistory(event);
    res.json(data);
  },
};

module.exports = metricsController;
