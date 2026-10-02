export const DATASET_UPDATE_EVENT = "habitsense_dataset_updated";

export function saveDataset(filename: string, headers: string[], data: any[]) {
  try {
    const payload = { filename, headers, data, updatedAt: Date.now() };
    localStorage.setItem('smarthome_dataset', JSON.stringify(payload));
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent(DATASET_UPDATE_EVENT, { detail: payload }));
    }
  } catch (e) {
    console.error("Failed to save dataset in localStorage", e);
  }
}

export function loadDataset() {
  try {
    const raw = localStorage.getItem('smarthome_dataset');
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

export function clearDatasetCache() {
  try {
    localStorage.removeItem('smarthome_dataset');
    if (typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent(DATASET_UPDATE_EVENT, { detail: null }));
    }
  } catch (e) {
    console.error("Failed to clear dataset cache", e);
  }
}

export async function fetchLatestDataset() {
  try {
    const res = await fetch("http://localhost:8000/api/current-dataset-raw", { cache: "no-store" });
    if (res.ok) {
      const data = await res.json();
      if (data.success && data.dataset) {
        saveDataset(data.dataset.filename, data.dataset.headers, data.dataset.data);
        return data.dataset;
      }
    }
  } catch (e) {
    console.error("Could not fetch latest dataset from backend", e);
  }
  return loadDataset();
}

export async function getOrFetchDataset(forceRefresh: boolean = false) {
  if (!forceRefresh) {
    const local = loadDataset();
    if (local && local.data && local.data.length > 0) return local;
  }
  return await fetchLatestDataset();
}

export function onDatasetUpdate(callback: (dataset: any) => void) {
  if (typeof window === "undefined") return () => {};
  const handler = (e: any) => {
    callback(e.detail || loadDataset());
  };
  window.addEventListener(DATASET_UPDATE_EVENT, handler);
  window.addEventListener("focus", handler);
  return () => {
    window.removeEventListener(DATASET_UPDATE_EVENT, handler);
    window.removeEventListener("focus", handler);
  };
}

export function detectFeatures(headers: string[]) {
  const h = headers.map(s => s.toLowerCase());
  return {
      timestamp: h.some(s => s.includes('time') || s.includes('date')),
      activity: h.some(s => s.includes('activity') || s.includes('label')),
      room: h.some(s => s.includes('room') || s.includes('location')),
      motion: h.some(s => s.includes('motion') || s.includes('pir')),
      door: h.some(s => s.includes('door') || s.includes('contact')),
      light: h.some(s => s.includes('light')),
      appliance: h.some(s => s.includes('tv') || s.includes('ac') || s.includes('appliance')),
      power: h.some(s => s.includes('power') || s.includes('energy') || s.includes('kw') || s.includes('watt')),
  };
}

export function calculateQuality(data: any[], headers: string[]) {
  if (!data || data.length === 0) return { missing: 0, score: 0 };
  let missing = 0;
  let total = data.length * headers.length;
  data.forEach(row => {
      headers.forEach(h => {
          if (row[h] === null || row[h] === undefined || row[h] === '') missing++;
      });
  });
  return {
      missing,
      score: Math.max(0, Math.round(((total - missing) / total) * 100))
  };
}
