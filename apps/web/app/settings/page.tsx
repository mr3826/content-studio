"use client";

import { useEffect, useState } from "react";
import { 
  ShieldCheck, 
  Layers, 
  Sparkles, 
  ExternalLink, 
  Download, 
  Upload, 
  Save, 
  Plus, 
  Trash2, 
  CheckCircle, 
  AlertCircle,
  RefreshCw,
  Brain,
  History,
  Play,
  Info,
  Tag
} from "lucide-react";
import { useLanguage } from "@/lib/LanguageContext";
import {
  getNiche,
  updateNiche,
  seedNiche,
  getNichePolicyAudits,
  dryRunNiche,
  getBrand,
  updateBrand,
  seedBrand,
  getBrandExemplars,
  createBrandExemplar,
  deleteBrandExemplar,
  getBrandMemory,
  recordBrandMemory,
  deleteBrandMemory,
  getPlatforms,
  updatePlatform,
  seedPlatforms,
  exportSettings,
  importSettings,
  seedAllSettings,
  NicheProfile,
  NichePolicyAudit,
  NicheDryRunResponse,
  NicheGuardVerdict,
  ContentPillar,
  TopicException,
  BrandProfile,
  BrandExemplar,
  BrandMemoryItem,
  PlatformSetting
} from "@/lib/api";

type Tab = "niche" | "brand" | "memory" | "exemplars" | "platforms" | "transfer";

export default function SettingsPage() {
  const { t, isBangla } = useLanguage();
  const [activeTab, setActiveTab] = useState<Tab>("niche");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  // Niche State
  const [niche, setNiche] = useState<NicheProfile>({
    name: "",
    one_sentence_definition: "",
    audience: "",
    target_skill_levels: [],
    audience_goals: [],
    audience_regions: [],
    primary_problems: [],
    allowed_topics: [],
    adjacent_topics: [],
    blocked_topics: [],
    topic_exceptions: [],
    must_have_signals: [],
    negative_keywords: [],
    preferred_source_types: [],
    content_pillars: [],
    commercial_intent_topics: [],
    evergreen_topics: [],
    policy_version: 1,
    policy_fingerprint: null,
  });
  const [policyAudits, setPolicyAudits] = useState<NichePolicyAudit[]>([]);
  const [testTopicInput, setTestTopicInput] = useState<string>("");
  const [testingTopic, setTestingTopic] = useState<boolean>(false);
  const [testDryRunResult, setTestDryRunResult] = useState<NicheDryRunResponse | null>(null);

  // Brand State
  const [brand, setBrand] = useState<BrandProfile>({
    brand_name: "",
    brand_promise: "",
    audience: "",
    tone: [],
    voice_rules: [],
    preferred_vocabulary: [],
    avoid_vocabulary: [],
    banned_cliches: [],
    claim_rules: [],
    cta_style: "",
    humor_policy: "",
    controversy_policy: "",
    sponsor_policy: "",
    affiliate_disclosure_style: "",
    default_lead_magnet: "",
    newsletter_cta: "",
    digital_product_cta: "",
    visual_identity: {},
    platform_adaptations: {},
  });

  // Brand Memory State
  const [memoryItems, setMemoryItems] = useState<BrandMemoryItem[]>([]);
  const [memoryFilter, setMemoryFilter] = useState<string>("all");
  const [newMemory, setNewMemory] = useState({
    memory_type: "hook",
    content: "",
  });

  // Exemplars State
  const [exemplars, setExemplars] = useState<BrandExemplar[]>([]);
  const [newExemplar, setNewExemplar] = useState({
    category: "approved_hook",
    title: "",
    content: "",
    platform: "all",
    context_note: "",
  });

  // Platforms State
  const [platforms, setPlatforms] = useState<Record<string, PlatformSetting>>({});

  // Transfer State
  const [importJson, setImportJson] = useState("");

  const loadAll = async () => {
    setLoading(true);
    try {
      const [nData, bData, exData, pData, mData, auditsData] = await Promise.all([
        getNiche(),
        getBrand(),
        getBrandExemplars(),
        getPlatforms(),
        getBrandMemory(),
        getNichePolicyAudits(10),
      ]);

      if (nData) setNiche(nData);
      if (bData) setBrand(bData);
      if (exData) setExemplars(exData);
      if (pData) setPlatforms(pData);
      if (mData) setMemoryItems(mData);
      if (auditsData) setPolicyAudits(auditsData);
    } catch (e) {
      console.error("Error loading settings:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const showToast = (type: "success" | "error", text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 4000);
  };

  // Niche Handlers
  const handleSaveNiche = async () => {
    setSaving(true);
    try {
      const updated = await updateNiche(niche);
      setNiche(updated);
      const audits = await getNichePolicyAudits(10);
      setPolicyAudits(audits);
      showToast("success", `Single Niche Profile saved! (Policy v${updated.policy_version || 1})`);
    } catch (e: any) {
      showToast("error", e.message || "Failed to save Niche Profile");
    } finally {
      setSaving(false);
    }
  };

  const handleSeedNiche = async () => {
    setSaving(true);
    try {
      const seeded = await seedNiche();
      setNiche(seeded);
      const audits = await getNichePolicyAudits(10);
      setPolicyAudits(audits);
      showToast("success", "Default Niche Profile seeded from template!");
    } catch (e: any) {
      showToast("error", e.message || "Failed to seed Niche");
    } finally {
      setSaving(false);
    }
  };

  // Niche Pillar & Exception Handlers
  const handleAddPillar = () => {
    const newId = `pillar_${Date.now()}`;
    const newPillar: ContentPillar = {
      id: newId,
      name: "",
      description: "",
      keywords: [],
      synonyms: [],
      examples: [],
    };
    setNiche({
      ...niche,
      content_pillars: [...(niche.content_pillars || []), newPillar],
    });
  };

  const handleUpdatePillar = (index: number, field: keyof ContentPillar, val: any) => {
    const updated = [...(niche.content_pillars || [])];
    updated[index] = { ...updated[index], [field]: val };
    setNiche({ ...niche, content_pillars: updated });
  };

  const handleDeletePillar = (index: number) => {
    const updated = (niche.content_pillars || []).filter((_, i) => i !== index);
    setNiche({ ...niche, content_pillars: updated });
  };

  const handleAddException = () => {
    const newException: TopicException = {
      topic: "",
      allowed_context: "educational_critique",
    };
    setNiche({
      ...niche,
      topic_exceptions: [...(niche.topic_exceptions || []), newException],
    });
  };

  const handleUpdateException = (index: number, field: keyof TopicException, val: string) => {
    const updated = [...(niche.topic_exceptions || [])];
    updated[index] = { ...updated[index], [field]: val };
    setNiche({ ...niche, topic_exceptions: updated });
  };

  const handleDeleteException = (index: number) => {
    const updated = (niche.topic_exceptions || []).filter((_, i) => i !== index);
    setNiche({ ...niche, topic_exceptions: updated });
  };

  const handleRunTestTopic = async (candidateText?: string) => {
    const textToTest = candidateText !== undefined ? candidateText : testTopicInput;
    if (!textToTest.trim()) return;
    setTestingTopic(true);
    try {
      const resp = await dryRunNiche({
        candidate_topics: [textToTest.trim()],
        proposed_profile: niche,
      });
      setTestDryRunResult(resp);
      showToast("success", "Topic dry run evaluation complete!");
    } catch (e: any) {
      showToast("error", e.message || "Dry run evaluation failed");
    } finally {
      setTestingTopic(false);
    }
  };

  // Brand Handlers
  const handleSaveBrand = async () => {
    setSaving(true);
    try {
      const updated = await updateBrand(brand);
      setBrand(updated);
      showToast("success", "Single Brand DNA saved successfully!");
    } catch (e: any) {
      showToast("error", e.message || "Failed to save Brand Profile");
    } finally {
      setSaving(false);
    }
  };

  const handleSeedBrand = async () => {
    setSaving(true);
    try {
      const seeded = await seedBrand();
      setBrand(seeded);
      showToast("success", "Default Brand DNA seeded from template!");
    } catch (e: any) {
      showToast("error", e.message || "Failed to seed Brand");
    } finally {
      setSaving(false);
    }
  };

  // Exemplar Handlers
  const handleAddExemplar = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newExemplar.title || !newExemplar.content) return;
    setSaving(true);
    try {
      const created = await createBrandExemplar(newExemplar);
      setExemplars([created, ...exemplars]);
      setNewExemplar({
        category: "approved_hook",
        title: "",
        content: "",
        platform: "all",
        context_note: "",
      });
      showToast("success", "Brand Exemplar added successfully!");
    } catch (e: any) {
      showToast("error", e.message || "Failed to add Exemplar");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteExemplar = async (id: string) => {
    try {
      await deleteBrandExemplar(id);
      setExemplars(exemplars.filter((x) => x.id !== id));
      showToast("success", "Brand Exemplar deleted.");
    } catch (e: any) {
      showToast("error", e.message || "Failed to delete Exemplar");
    }
  };

  // Brand Memory Handlers
  const handleAddMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMemory.content.trim()) return;
    setSaving(true);
    try {
      const created = await recordBrandMemory({
        memory_type: newMemory.memory_type,
        content: newMemory.content.trim(),
      });
      setMemoryItems([created, ...memoryItems.filter((m) => m.id !== created.id)]);
      setNewMemory({
        memory_type: "hook",
        content: "",
      });
      showToast("success", "Brand memory recorded successfully!");
    } catch (e: any) {
      showToast("error", e.message || "Failed to record Brand Memory");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteMemory = async (id: string) => {
    try {
      await deleteBrandMemory(id);
      setMemoryItems(memoryItems.filter((m) => m.id !== id));
      showToast("success", "Brand memory item removed.");
    } catch (e: any) {
      showToast("error", e.message || "Failed to remove Brand Memory item");
    }
  };

  // Platform Handlers
  const handleSavePlatform = async (platName: string) => {
    const plat = platforms[platName];
    if (!plat) return;

    if (plat.channel_url && !plat.channel_url.startsWith("https://")) {
      showToast("error", `Channel URL for ${platName} must start with https://`);
      return;
    }
    if (plat.publishing_url && !plat.publishing_url.startsWith("https://")) {
      showToast("error", `Publishing URL for ${platName} must start with https://`);
      return;
    }

    setSaving(true);
    try {
      const updated = await updatePlatform(platName, plat);
      setPlatforms({ ...platforms, [platName]: updated });
      showToast("success", `${platName.toUpperCase()} launcher settings saved.`);
    } catch (e: any) {
      showToast("error", e.message || `Failed to update ${platName}`);
    } finally {
      setSaving(false);
    }
  };

  const handleSeedPlatforms = async () => {
    setSaving(true);
    try {
      const seeded = await seedPlatforms();
      setPlatforms(seeded);
      showToast("success", "Platform Launchers seeded from template!");
    } catch (e: any) {
      showToast("error", e.message || "Failed to seed platforms");
    } finally {
      setSaving(false);
    }
  };

  // Transfer Handlers
  const handleExport = async () => {
    try {
      const data = await exportSettings();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `content-studio-config-${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("success", "Configuration exported successfully!");
    } catch (e: any) {
      showToast("error", e.message || "Export failed");
    }
  };

  const handleImport = async () => {
    if (!importJson.trim()) return;
    setSaving(true);
    try {
      const parsed = JSON.parse(importJson);
      await importSettings(parsed);
      await loadAll();
      setImportJson("");
      showToast("success", "Configuration imported and applied!");
    } catch (e: any) {
      showToast("error", e.message || "Invalid JSON or Import Failed");
    } finally {
      setSaving(false);
    }
  };

  const handleSeedAll = async () => {
    if (!confirm("Seed all default configs (Niche, Brand, Platforms)?")) return;
    setSaving(true);
    try {
      await seedAllSettings();
      await loadAll();
      showToast("success", "All studio defaults seeded successfully!");
    } catch (e: any) {
      showToast("error", e.message || "Seed all failed");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        <RefreshCw className="w-5 h-5 animate-spin mr-2" />
        Loading studio settings...
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Toast */}
      {message && (
        <div
          className={`p-4 rounded-xl flex items-center justify-between border ${
            message.type === "success"
              ? "bg-emerald-950/80 border-emerald-800 text-emerald-300"
              : "bg-red-950/80 border-red-800 text-red-300"
          }`}
        >
          <div className="flex items-center gap-2">
            {message.type === "success" ? (
              <CheckCircle className="w-5 h-5 text-emerald-400" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-400" />
            )}
            <span className="text-sm font-medium">{message.text}</span>
          </div>
          <button onClick={() => setMessage(null)} className="text-xs text-slate-400 hover:text-white">
            &times;
          </button>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Studio Settings</h1>
          <p className="text-sm text-slate-400">
            Configure the single niche, single brand identity, brand exemplars, and platform launchers.
          </p>
        </div>
        <button
          onClick={handleSeedAll}
          disabled={saving}
          className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 hover:bg-indigo-600/30 transition-colors"
        >
          Seed All Defaults
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2 overflow-x-auto no-scrollbar whitespace-nowrap">
        <button
          onClick={() => setActiveTab("niche")}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2 ${
            activeTab === "niche"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Single Niche
        </button>

        <button
          onClick={() => setActiveTab("brand")}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2 ${
            activeTab === "brand"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <Layers className="w-4 h-4" />
          Brand DNA
        </button>

        <button
          onClick={() => setActiveTab("memory")}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2 ${
            activeTab === "memory"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <Brain className="w-4 h-4" />
          Brand Memory ({memoryItems.length})
        </button>

        <button
          onClick={() => setActiveTab("exemplars")}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2 ${
            activeTab === "exemplars"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <Sparkles className="w-4 h-4" />
          Brand Exemplars ({exemplars.length})
        </button>

        <button
          onClick={() => setActiveTab("platforms")}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2 ${
            activeTab === "platforms"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <ExternalLink className="w-4 h-4" />
          Platform Launchers
        </button>

        <button
          onClick={() => setActiveTab("transfer")}
          className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors flex items-center gap-2 ${
            activeTab === "transfer"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-800/60"
          }`}
        >
          <Download className="w-4 h-4" />
          Export / Import
        </button>
      </div>

      {/* Tab 1: Single Niche */}
      {activeTab === "niche" && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-8">
          {/* Top Bar with Policy Version and Actions */}
          <div className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-4 gap-4">
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-base font-semibold text-white">
                  {t("settings.nicheTab.title", "Single Niche Profile")}
                </h2>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Policy v{niche.policy_version || 1}
                </span>
                {niche.policy_fingerprint && (
                  <span className="hidden sm:inline-flex items-center font-mono text-[11px] text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60" title={niche.policy_fingerprint}>
                    SHA: {niche.policy_fingerprint.slice(0, 10)}...
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-1">
                {t("settings.nicheTab.subtitle", "In accordance with invariant #1, exactly one active niche profile guides discovery, opportunity scoring, and quality gates.")}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleSeedNiche}
                disabled={saving}
                className="px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-colors"
              >
                {t("settings.nicheTab.seedExample", "Seed Example Niche")}
              </button>
              <button
                type="button"
                onClick={handleSaveNiche}
                disabled={saving}
                className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition-colors"
              >
                <Save className="w-3.5 h-3.5" />
                {saving ? t("common.saving", "Saving...") : t("settings.nicheTab.save", "Save Niche Profile")}
              </button>
            </div>
          </div>

          {/* Policy Invariant & Revision Notice */}
          <div className="p-3.5 rounded-xl bg-indigo-950/20 border border-indigo-800/30 text-xs text-indigo-300 flex items-start gap-2.5">
            <Info className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold">{t("settings.nicheTab.materialChangeNotice", "Material changes increment policy version and are tracked in audit history.")}</span>{" "}
              Changes to allowed, adjacent, or blocked topics will recalculate subsequent discovery candidates and invalidate stale Quality Gate assessments.
            </div>
          </div>

          {/* Section 1: Core Definition & Audience Profile */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
              1. Core Definition & Audience Target
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {t("settings.nicheTab.name", "Niche Name")}
                </label>
                <input
                  type="text"
                  value={niche.name}
                  onChange={(e) => setNiche({ ...niche, name: e.target.value })}
                  placeholder="e.g. AI Engineering & Coding Automation"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {t("settings.nicheTab.targetAudience", "Target Audience")}
                </label>
                <input
                  type="text"
                  value={niche.audience}
                  onChange={(e) => setNiche({ ...niche, audience: e.target.value })}
                  placeholder="e.g. Software engineers, technical founders, automation builders"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {t("settings.nicheTab.skillLevels", "Target Skill Levels (Comma-separated)")}
                </label>
                <input
                  type="text"
                  value={(niche.target_skill_levels || []).join(", ")}
                  onChange={(e) =>
                    setNiche({
                      ...niche,
                      target_skill_levels: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="intermediate, advanced, professional"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {t("settings.nicheTab.goals", "Audience Goals (Comma-separated)")}
                </label>
                <input
                  type="text"
                  value={(niche.audience_goals || []).join(", ")}
                  onChange={(e) =>
                    setNiche({
                      ...niche,
                      audience_goals: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="automate routine code refactoring, build reliable local agent pipelines"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {t("settings.nicheTab.definition", "One-Sentence Definition")}
                </label>
                <textarea
                  rows={2}
                  value={niche.one_sentence_definition}
                  onChange={(e) => setNiche({ ...niche, one_sentence_definition: e.target.value })}
                  placeholder="Practical AI coding agents, developer automation workflows, and local LLM tooling tested on production tasks."
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {t("settings.nicheTab.primaryProblems", "Primary Audience Problems (Comma-separated)")}
                </label>
                <input
                  type="text"
                  value={(niche.primary_problems || []).join(", ")}
                  onChange={(e) =>
                    setNiche({
                      ...niche,
                      primary_problems: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="brittle prompts breaking in production, high API costs, hallucinated code"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Section 2: Editorial Topic Boundaries & Signals */}
          <div className="space-y-4 pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
              2. Editorial Topic Boundaries & Alignment Signals
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {t("settings.nicheTab.allowedTopics", "Allowed Core Topics (Comma-separated)")}
                </label>
                <input
                  type="text"
                  value={(niche.allowed_topics || []).join(", ")}
                  onChange={(e) =>
                    setNiche({
                      ...niche,
                      allowed_topics: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="coding agents, local LLMs, developer tools, test automation"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs font-medium text-slate-300">
                    {t("settings.nicheTab.adjacentTopics", "Relevant Adjacent Topics (Comma-separated)")}
                  </label>
                  <span className="text-[10px] text-sky-400">Allowed for context (not penalized)</span>
                </div>
                <input
                  type="text"
                  value={(niche.adjacent_topics || []).join(", ")}
                  onChange={(e) =>
                    setNiche({
                      ...niche,
                      adjacent_topics: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="database indexing, devops pipelines, API design"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs font-medium text-slate-300">
                    {t("settings.nicheTab.blockedTopics", "Blocked Topics (Instant Block)")}
                  </label>
                  <span className="text-[10px] text-rose-400">Hard reject unless educational critique</span>
                </div>
                <input
                  type="text"
                  value={(niche.blocked_topics || []).join(", ")}
                  onChange={(e) =>
                    setNiche({
                      ...niche,
                      blocked_topics: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="crypto trading, get rich quick, passive income schemes, celebrity gossip"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {t("settings.nicheTab.negativeKeywords", "Negative Keywords (Hype / Low-value Signals)")}
                </label>
                <input
                  type="text"
                  value={(niche.negative_keywords || []).join(", ")}
                  onChange={(e) =>
                    setNiche({
                      ...niche,
                      negative_keywords: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="secret trick, replaced all coders, 100x money, guaranteed success"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {t("settings.nicheTab.mustHaveSignals", "Must-Have Signals (Bonus Alignment Indicators)")}
                </label>
                <input
                  type="text"
                  value={(niche.must_have_signals || []).join(", ")}
                  onChange={(e) =>
                    setNiche({
                      ...niche,
                      must_have_signals: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="benchmark, reproducible, architecture, production-grade"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  {t("settings.nicheTab.evergreenTopics", "Evergreen Topics")}
                </label>
                <input
                  type="text"
                  value={(niche.evergreen_topics || []).join(", ")}
                  onChange={(e) =>
                    setNiche({
                      ...niche,
                      evergreen_topics: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="python debugging, unit testing best practices, sqlite wal mode"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Section 3: Topic Exceptions (Contextual Critiques / Debunks) */}
          <div className="space-y-4 pt-4 border-t border-slate-800">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
                  3. {t("settings.nicheTab.topicExceptions", "Topic Exceptions (Contextual Critiques & Myth-Busting)")}
                </h3>
                <p className="text-xs text-slate-400">
                  Allow specific blocked terms when explicitly framed as educational debunking, myth-busting, or critical review.
                </p>
              </div>
              <button
                type="button"
                onClick={handleAddException}
                className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700"
              >
                <Plus className="w-3.5 h-3.5" />
                {t("settings.nicheTab.addException", "Add Exception")}
              </button>
            </div>

            {(niche.topic_exceptions || []).length === 0 ? (
              <p className="text-xs text-slate-400 italic">No custom topic exceptions configured.</p>
            ) : (
              <div className="space-y-2">
                {(niche.topic_exceptions || []).map((exc, idx) => (
                  <div key={idx} className="flex items-center gap-3 p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <input
                      type="text"
                      value={exc.topic}
                      onChange={(e) => handleUpdateException(idx, "topic", e.target.value)}
                      placeholder="Topic (e.g. passive income)"
                      className="flex-1 px-2.5 py-1 text-xs rounded bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-indigo-500"
                    />
                    <input
                      type="text"
                      value={exc.allowed_context}
                      onChange={(e) => handleUpdateException(idx, "allowed_context", e.target.value)}
                      placeholder="Allowed Context (e.g. educational_critique)"
                      className="flex-1 px-2.5 py-1 text-xs rounded bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-indigo-500"
                    />
                    <button
                      type="button"
                      onClick={() => handleDeleteException(idx)}
                      className="p-1 text-slate-400 hover:text-red-400 transition-colors"
                      title="Remove Exception"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Section 4: Content Pillars (Enriched v1.02) */}
          <div className="space-y-4 pt-4 border-t border-slate-800">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
                  4. {t("settings.nicheTab.contentPillars", "Content Pillars (Enriched Taxonomy)")}
                </h3>
                <p className="text-xs text-slate-400">
                  Core editorial categories with dedicated matching keywords, synonyms, and objective descriptions.
                </p>
              </div>
              <button
                type="button"
                onClick={handleAddPillar}
                className="flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700"
              >
                <Plus className="w-3.5 h-3.5" />
                {t("settings.nicheTab.addPillar", "Add Pillar")}
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(niche.content_pillars || []).map((pillar, idx) => (
                <div key={pillar.id || idx} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-mono text-indigo-400 bg-indigo-950/40 px-2 py-0.5 rounded border border-indigo-800/40">
                      #{pillar.id}
                    </span>
                    <button
                      type="button"
                      onClick={() => handleDeletePillar(idx)}
                      className="text-slate-400 hover:text-red-400 p-1 transition-colors"
                      title="Delete Pillar"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
                      {t("settings.nicheTab.pillarName", "Pillar Name")}
                    </label>
                    <input
                      type="text"
                      value={pillar.name}
                      onChange={(e) => handleUpdatePillar(idx, "name", e.target.value)}
                      placeholder="e.g. AI Coding Agents"
                      className="w-full px-2.5 py-1.5 text-xs rounded bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
                      {t("settings.nicheTab.pillarDesc", "Description")}
                    </label>
                    <textarea
                      rows={2}
                      value={pillar.description}
                      onChange={(e) => handleUpdatePillar(idx, "description", e.target.value)}
                      placeholder="Hands-on evaluations, benchmarks, and architectural patterns for autonomous agents."
                      className="w-full px-2.5 py-1.5 text-xs rounded bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
                        {t("settings.nicheTab.pillarKeywords", "Keywords")}
                      </label>
                      <input
                        type="text"
                        value={(pillar.keywords || []).join(", ")}
                        onChange={(e) =>
                          handleUpdatePillar(
                            idx,
                            "keywords",
                            e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
                          )
                        }
                        placeholder="agents, autonomous, benchmarks"
                        className="w-full px-2 py-1 text-xs rounded bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-400 uppercase mb-1">
                        {t("settings.nicheTab.pillarSynonyms", "Synonyms")}
                      </label>
                      <input
                        type="text"
                        value={(pillar.synonyms || []).join(", ")}
                        onChange={(e) =>
                          handleUpdatePillar(
                            idx,
                            "synonyms",
                            e.target.value.split(",").map((s) => s.trim()).filter(Boolean)
                          )
                        }
                        placeholder="agentic AI, coding assistants"
                        className="w-full px-2 py-1 text-xs rounded bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-indigo-500"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 5: Live Dry Run & Topic Alignment Tester */}
          <div className="space-y-4 pt-4 border-t border-slate-800">
            <div>
              <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
                <Play className="w-4 h-4 text-emerald-400" />
                5. {t("settings.nicheTab.dryRunTitle", "Topic Test & Dry Run Preview")}
              </h3>
              <p className="text-xs text-slate-400">
                {t("settings.nicheTab.dryRunSubtitle", "Test candidate topics against current or proposed rules before saving.")}
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
              <input
                type="text"
                value={testTopicInput}
                onChange={(e) => setTestTopicInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleRunTestTopic();
                  }
                }}
                placeholder={t("settings.nicheTab.testInputPlaceholder", "Enter candidate topic or title to test...")}
                className="flex-1 px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
              />
              <button
                type="button"
                onClick={() => handleRunTestTopic()}
                disabled={testingTopic || !testTopicInput.trim()}
                className="flex items-center justify-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white shadow-md shadow-emerald-600/20 transition-colors"
              >
                <Play className="w-3.5 h-3.5" />
                {testingTopic ? t("common.running", "Evaluating...") : t("settings.nicheTab.runDryRun", "Test Topic")}
              </button>
            </div>

            {/* Quick Test Chips */}
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-[11px] text-slate-400 mr-1">Quick Test:</span>
              {[
                "Benchmarking AI coding agents on large legacy repositories",
                "Why database indexing matters when building AI agent memory",
                "Why AI trading bots cannot guarantee passive income",
                "Guaranteed 100x crypto trading bot profit scheme",
                "How to make artisan sourdough bread at home",
              ].map((sample, sIdx) => (
                <button
                  key={sIdx}
                  type="button"
                  onClick={() => {
                    setTestTopicInput(sample);
                    handleRunTestTopic(sample);
                  }}
                  className="px-2 py-1 text-[11px] rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60 transition-colors"
                >
                  {sample.length > 40 ? sample.slice(0, 38) + "..." : sample}
                </button>
              ))}
            </div>

            {/* Dry Run Result Display */}
            {testDryRunResult && testDryRunResult.results.length > 0 && (
              <div className="mt-4 p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
                {testDryRunResult.results.map((res, rIdx) => {
                  const v = res.verdict;
                  const classificationColors: Record<string, string> = {
                    core_niche: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
                    adjacent: "bg-sky-500/20 text-sky-400 border-sky-500/30",
                    ambiguous: "bg-amber-500/20 text-amber-400 border-amber-500/30",
                    blocked: "bg-rose-500/20 text-rose-400 border-rose-500/30",
                    off_niche: "bg-slate-500/20 text-slate-400 border-slate-500/30",
                  };
                  const badgeColor = classificationColors[v.classification || ""] || (v.passed ? classificationColors.core_niche : classificationColors.blocked);

                  return (
                    <div key={rIdx} className="space-y-3">
                      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
                        <div className="flex items-center gap-2">
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeColor}`}>
                            {v.classification?.toUpperCase() || (v.passed ? "PASSED" : "REJECTED")}
                          </span>
                          <span className="text-xs font-bold text-white">
                            Score: {v.score}/100
                          </span>
                          {v.requires_review && (
                            <span className="px-2 py-0.5 rounded text-[11px] bg-amber-950/40 text-amber-300 border border-amber-700/40">
                              Review Required
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-slate-400 font-mono">
                          Policy v{v.policy_version || niche.policy_version || 1}
                        </span>
                      </div>

                      <div className="text-xs text-slate-300">
                        <span className="font-semibold text-white">Reason:</span> {v.reason}
                      </div>

                      {v.requires_review && v.review_reasons && v.review_reasons.length > 0 && (
                        <div className="p-2 rounded bg-amber-950/20 border border-amber-900/30 text-xs text-amber-300">
                          <span className="font-semibold">Review reasons:</span> {v.review_reasons.join("; ")}
                        </div>
                      )}

                      {/* 5-Dimension Audience Value Breakdown */}
                      {v.audience_value_breakdown && (
                        <div className="pt-2">
                          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                            Audience Value Breakdown:
                          </span>
                          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                            {Object.entries(v.audience_value_breakdown).map(([dim, score]) => (
                              <div key={dim} className="p-2 rounded bg-slate-900/80 border border-slate-800 text-center">
                                <span className="block text-[10px] text-slate-400 capitalize">
                                  {dim.replace("_", " ")}
                                </span>
                                <span className="text-xs font-bold text-indigo-300">
                                  {score}/100
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Platform Warning Metadata if any */}
                      {v.platform_warning_metadata?.notes && v.platform_warning_metadata.notes.length > 0 && (
                        <div className="p-2 rounded bg-slate-900 text-xs text-slate-400 border border-slate-800">
                          <span className="font-semibold text-slate-300">Platform Warning Note:</span>{" "}
                          {v.platform_warning_metadata.notes.join("; ")}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Section 6: Policy Revision Audit History */}
          <div className="space-y-4 pt-4 border-t border-slate-800">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <History className="w-4 h-4 text-slate-400" />
              6. {t("settings.nicheTab.policyHistoryTitle", "Policy Revision Audit History")}
            </h3>
            <p className="text-xs text-slate-400">
              Immutable records of material changes to topic boundaries, pillars, and negative keywords.
            </p>

            {policyAudits.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No revision audit logs recorded yet.</p>
            ) : (
              <div className="space-y-2">
                {policyAudits.map((audit) => (
                  <div key={audit.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-indigo-400">
                          v{audit.policy_version}
                        </span>
                        {audit.material_change ? (
                          <span className="px-1.5 py-0.5 rounded text-[10px] bg-indigo-950 text-indigo-300 border border-indigo-800">
                            Material Update
                          </span>
                        ) : (
                          <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-900 text-slate-400 border border-slate-800">
                            Minor Update
                          </span>
                        )}
                        <span className="text-slate-300 font-medium">{audit.change_summary}</span>
                      </div>
                      {audit.diff_fields && audit.diff_fields.length > 0 && (
                        <div className="text-[11px] text-slate-400">
                          Fields changed: {audit.diff_fields.join(", ")}
                        </div>
                      )}
                    </div>
                    <div className="text-right text-[11px] text-slate-400 font-mono shrink-0">
                      <div>{new Date(audit.created_at).toLocaleString()}</div>
                      <div title={audit.policy_fingerprint}>SHA: {audit.policy_fingerprint?.slice(0, 10)}...</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Brand DNA */}
      {activeTab === "brand" && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Single Brand DNA</h2>
              <p className="text-xs text-slate-400">
                All scripts, narration, captions, and visual rules inherit this brand identity.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleSeedBrand}
                disabled={saving}
                className="px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
              >
                Seed Example Brand
              </button>
              <button
                type="button"
                onClick={handleSaveBrand}
                disabled={saving}
                className="flex items-center gap-1.5 px-4 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20"
              >
                <Save className="w-3.5 h-3.5" />
                {saving ? "Saving..." : "Save Brand Profile"}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Brand Name
                </label>
                <input
                  type="text"
                  value={brand.brand_name}
                  onChange={(e) => setBrand({ ...brand, brand_name: e.target.value })}
                  placeholder="e.g. Practical AI Studio"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Brand Promise
                </label>
                <input
                  type="text"
                  value={brand.brand_promise}
                  onChange={(e) => setBrand({ ...brand, brand_promise: e.target.value })}
                  placeholder="Tested AI tools, automated workflows, and honest benchmarks without hype."
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Tone Attributes (Comma-separated)
                </label>
                <input
                  type="text"
                  value={brand.tone.join(", ")}
                  onChange={(e) =>
                    setBrand({
                      ...brand,
                      tone: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="evidence-driven, concise, practical, calm, transparent"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Preferred Vocabulary
                </label>
                <input
                  type="text"
                  value={brand.preferred_vocabulary.join(", ")}
                  onChange={(e) =>
                    setBrand({
                      ...brand,
                      preferred_vocabulary: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="benchmark, latency, trade-off, failure rate, reproducible"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Avoid Vocabulary (Hype words)
                </label>
                <input
                  type="text"
                  value={brand.avoid_vocabulary.join(", ")}
                  onChange={(e) =>
                    setBrand({
                      ...brand,
                      avoid_vocabulary: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="game-changer, insane, mind-blowing, unbelievable"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Banned Clichés
                </label>
                <input
                  type="text"
                  value={brand.banned_cliches.join(", ")}
                  onChange={(e) =>
                    setBrand({
                      ...brand,
                      banned_cliches: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="In today's fast-paced world..., Without further ado..."
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Claim Rules
                </label>
                <input
                  type="text"
                  value={brand.claim_rules.join(", ")}
                  onChange={(e) =>
                    setBrand({
                      ...brand,
                      claim_rules: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
                    })
                  }
                  placeholder="Every speed claim must cite a benchmark run or primary source."
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  CTA Style
                </label>
                <input
                  type="text"
                  value={brand.cta_style}
                  onChange={(e) => setBrand({ ...brand, cta_style: e.target.value })}
                  placeholder="Direct, educational, and low-friction"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          </div>

          {/* Monetization & Conversion CTAs */}
          <div className="border-t border-slate-800 pt-6">
            <h3 className="text-sm font-semibold text-white mb-1">Monetization & Conversion CTAs</h3>
            <p className="text-xs text-slate-400 mb-4">
              Configured lead magnets, newsletter hooks, and digital product CTAs automatically available to content engines.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Default Lead Magnet CTA
                </label>
                <input
                  type="text"
                  value={brand.default_lead_magnet || ""}
                  onChange={(e) => setBrand({ ...brand, default_lead_magnet: e.target.value })}
                  placeholder="e.g. Free Local AI Architecture Guide (local-ai.guide)"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Newsletter CTA
                </label>
                <input
                  type="text"
                  value={brand.newsletter_cta || ""}
                  onChange={(e) => setBrand({ ...brand, newsletter_cta: e.target.value })}
                  placeholder="e.g. Subscribe to the Fresh AI Weekly Brief for benchmark datasets"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Digital Product CTA
                </label>
                <input
                  type="text"
                  value={brand.digital_product_cta || ""}
                  onChange={(e) => setBrand({ ...brand, digital_product_cta: e.target.value })}
                  placeholder="e.g. Download the Complete Local Studio Starter Kit ($49)"
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab: Brand Memory & Repetition */}
      {activeTab === "memory" && (
        <div className="space-y-6">
          {/* Header & Add Memory Form */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h2 className="text-base font-semibold text-white mb-1">Record Brand Memory</h2>
            <p className="text-xs text-slate-400 mb-4">
              Persistent memory store for hooks, CTAs, topics, tested products, and conclusions. Brand QA queries this memory to prevent repetition and ensure brand continuity.
            </p>

            <form onSubmit={handleAddMemory} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Memory Type
                  </label>
                  <select
                    value={newMemory.memory_type}
                    onChange={(e) => setNewMemory({ ...newMemory, memory_type: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="hook">Hook</option>
                    <option value="cta">CTA</option>
                    <option value="topic">Topic</option>
                    <option value="tested_product">Tested Product</option>
                    <option value="conclusion">Conclusion</option>
                    <option value="visual_pattern">Visual Pattern</option>
                    <option value="frequent_phrase">Frequent Phrase</option>
                    <option value="thumbnail_wording">Thumbnail Wording</option>
                  </select>
                </div>

                <div className="md:col-span-3">
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Content / Pattern
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newMemory.content}
                      onChange={(e) => setNewMemory({ ...newMemory, content: e.target.value })}
                      placeholder="e.g. Stop paying OpenAI for batch summarization when Ollama 3.1 is 10x faster."
                      className="flex-1 px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                    />
                    <button
                      type="submit"
                      disabled={saving || !newMemory.content.trim()}
                      className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white whitespace-nowrap"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      Add to Memory
                    </button>
                  </div>
                </div>
              </div>
            </form>
          </div>

          {/* Filter Chips */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {[
              { id: "all", label: "All Items" },
              { id: "hook", label: "Hooks" },
              { id: "cta", label: "CTAs" },
              { id: "topic", label: "Topics" },
              { id: "tested_product", label: "Tested Products" },
              { id: "conclusion", label: "Conclusions" },
              { id: "visual_pattern", label: "Visuals" },
              { id: "frequent_phrase", label: "Phrases" },
              { id: "thumbnail_wording", label: "Thumbnails" },
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setMemoryFilter(f.id)}
                className={`px-3 py-1.5 text-xs font-medium rounded-full transition-colors whitespace-nowrap ${
                  memoryFilter === f.id
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-white"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Memory Items List */}
          <div className="space-y-3">
            {memoryItems
              .filter((m) => memoryFilter === "all" || m.memory_type === memoryFilter)
              .length === 0 ? (
              <div className="p-8 text-center text-sm text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
                No brand memory recorded in this category yet. Memory items are automatically recorded upon script approval or manually above.
              </div>
            ) : (
              memoryItems
                .filter((m) => memoryFilter === "all" || m.memory_type === memoryFilter)
                .map((item) => (
                  <div
                    key={item.id}
                    className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start justify-between gap-4"
                  >
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded bg-indigo-950 text-indigo-400 border border-indigo-800">
                          {item.memory_type.replace("_", " ")}
                        </span>
                        <span className="text-[11px] text-slate-400">
                          Used {item.usage_count} {item.usage_count === 1 ? "time" : "times"}
                        </span>
                        <span className="text-[11px] text-slate-400">
                          • Last used: {new Date(item.last_used_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm text-slate-200">{item.content}</p>
                    </div>

                    <button
                      onClick={() => handleDeleteMemory(item.id)}
                      className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-950/30 rounded-lg transition-colors"
                      title="Delete Memory Item"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))
            )}
          </div>
        </div>
      )}

      {/* Tab 3: Brand Exemplars */}
      {activeTab === "exemplars" && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
            <h2 className="text-base font-semibold text-white mb-1">Add Brand Exemplar</h2>
            <p className="text-xs text-slate-400 mb-4">
              Reference examples of approved hooks, scripts, captions, and do/don't guidelines.
            </p>

            <form onSubmit={handleAddExemplar} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Category
                  </label>
                  <select
                    value={newExemplar.category}
                    onChange={(e) => setNewExemplar({ ...newExemplar, category: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="approved_hook">Approved Hook</option>
                    <option value="approved_script">Approved Script</option>
                    <option value="approved_caption">Approved Caption</option>
                    <option value="do_example">Do Example</option>
                    <option value="dont_example">Don't Example</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    required
                    value={newExemplar.title}
                    onChange={(e) => setNewExemplar({ ...newExemplar, title: e.target.value })}
                    placeholder="e.g. Coding Agent Stress Test Hook"
                    className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                    Platform
                  </label>
                  <select
                    value={newExemplar.platform}
                    onChange={(e) => setNewExemplar({ ...newExemplar, platform: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="all">All Platforms</option>
                    <option value="youtube">YouTube</option>
                    <option value="facebook">Facebook</option>
                    <option value="instagram">Instagram</option>
                    <option value="tiktok">TikTok</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Exemplar Content
                </label>
                <textarea
                  required
                  rows={3}
                  value={newExemplar.content}
                  onChange={(e) => setNewExemplar({ ...newExemplar, content: e.target.value })}
                  placeholder="Paste exemplar text or script snippet here..."
                  className="w-full px-3 py-2 text-sm rounded-lg bg-slate-950 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={saving}
                  className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Add Exemplar
                </button>
              </div>
            </form>
          </div>

          {/* List */}
          <div className="space-y-3">
            {exemplars.length === 0 ? (
              <div className="p-8 text-center text-sm text-slate-500 border border-dashed border-slate-800 rounded-xl">
                No brand exemplars added yet. Add approved hooks and scripts to guide generation quality.
              </div>
            ) : (
              exemplars.map((ex) => (
                <div key={ex.id} className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {ex.category.replace("_", " ").toUpperCase()}
                      </span>
                      <span className="text-xs font-medium text-slate-400">Platform: {ex.platform}</span>
                      <span className="text-sm font-semibold text-white">{ex.title}</span>
                    </div>
                    <p className="text-xs text-slate-300 whitespace-pre-wrap">{ex.content}</p>
                  </div>
                  <button
                    onClick={() => handleDeleteExemplar(ex.id)}
                    className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab 4: Platform Launchers */}
      {activeTab === "platforms" && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Platform Launchers (Manual V1)</h2>
              <p className="text-xs text-slate-400">
                Configure direct channel and publishing URLs for YouTube, Facebook, Instagram, and TikTok. (HTTPS required).
              </p>
            </div>
            <button
              onClick={handleSeedPlatforms}
              disabled={saving}
              className="px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
            >
              Seed Example URLs
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {["youtube", "facebook", "instagram", "tiktok"].map((pName) => {
              const p = platforms[pName] || {
                platform: pName,
                channel_name: "",
                channel_url: "",
                publishing_url: "",
                account_handle: "",
                is_active: true,
              };

              return (
                <div key={pName} className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold uppercase tracking-wider text-indigo-400">
                      {pName}
                    </span>
                    <div className="flex items-center gap-2">
                      {p.publishing_url && (
                        <a
                          href={p.publishing_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-[11px] font-medium text-slate-400 hover:text-sky-400 transition-colors"
                        >
                          <span>Test Open</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      <button
                        onClick={() => handleSavePlatform(pName)}
                        disabled={saving}
                        className="px-2.5 py-1 text-xs font-semibold rounded bg-slate-800 hover:bg-slate-700 text-white border border-slate-700"
                      >
                        Save
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-0.5">Channel Name</label>
                    <input
                      type="text"
                      value={p.channel_name}
                      onChange={(e) =>
                        setPlatforms({
                          ...platforms,
                          [pName]: { ...p, channel_name: e.target.value },
                        })
                      }
                      placeholder={`e.g. My ${pName} Channel`}
                      className="w-full px-2.5 py-1.5 text-xs rounded bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-0.5">Publishing / Studio URL (HTTPS)</label>
                    <input
                      type="text"
                      value={p.publishing_url}
                      onChange={(e) =>
                        setPlatforms({
                          ...platforms,
                          [pName]: { ...p, publishing_url: e.target.value },
                        })
                      }
                      placeholder="https://studio.youtube.com/"
                      className="w-full px-2.5 py-1.5 text-xs rounded bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-[11px] font-medium text-slate-400 mb-0.5">Public Channel URL (HTTPS)</label>
                    <input
                      type="text"
                      value={p.channel_url}
                      onChange={(e) =>
                        setPlatforms({
                          ...platforms,
                          [pName]: { ...p, channel_url: e.target.value },
                        })
                      }
                      placeholder="https://www.youtube.com/@mychannel"
                      className="w-full px-2.5 py-1.5 text-xs rounded bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 5: Transfer */}
      {activeTab === "transfer" && (
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-6">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-base font-semibold text-white">Export & Import Configuration</h2>
            <p className="text-xs text-slate-400">
              Download your Single Niche Profile, Brand DNA, and Platform settings as portable JSON or restore from backup.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Download className="w-4 h-4 text-indigo-400" />
                Export Configuration
              </h3>
              <p className="text-xs text-slate-400">
                Downloads an atomic snapshot of your studio's active niche, brand profile, exemplars, and platform URLs.
              </p>
              <button
                onClick={handleExport}
                className="w-full py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
              >
                Download Config JSON
              </button>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Upload className="w-4 h-4 text-sky-400" />
                Import Configuration
              </h3>
              <p className="text-xs text-slate-400">
                Paste JSON content to restore or apply external configuration.
              </p>
              <textarea
                rows={4}
                value={importJson}
                onChange={(e) => setImportJson(e.target.value)}
                placeholder='{"niche": {...}, "brand": {...}}'
                className="w-full p-2 text-xs font-mono rounded bg-slate-900 border border-slate-800 text-white focus:outline-none focus:border-indigo-500"
              />
              <button
                onClick={handleImport}
                disabled={saving || !importJson.trim()}
                className="w-full py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 disabled:opacity-50 transition-colors"
              >
                Apply Imported JSON
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
