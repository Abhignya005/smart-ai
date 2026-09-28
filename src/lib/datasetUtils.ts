export function saveDataset(filename: string, headers: string[], data: any[]) {
  localStorage.setItem('smarthome_dataset', JSON.stringify({ filename, headers, data }));
}

export function loadDataset() {
  const raw = localStorage.getItem('smarthome_dataset');
  if (!raw) return null;
  return JSON.parse(raw);
}

export function detectFeatures(headers: string[]) {
  const h = headers.map(s => s.toLowerCase());
  return {
      timestamp: h.some(s => s.includes('time') || s.includes('date')),
      activity: h.some(s => s.includes('activity')),
      room: h.some(s => s.includes('room') || s.includes('location')),
      motion: h.some(s => s.includes('motion') || s.includes('pir')),
      door: h.some(s => s.includes('door') || s.includes('contact')),
      light: h.some(s => s.includes('light')),
      appliance: h.some(s => s.includes('tv') || s.includes('ac') || s.includes('appliance')),
      power: h.some(s => s.includes('power') || s.includes('energy') || s.includes('kw') || s.includes('watt')),
  };
}

export function calculateQuality(data: any[], headers: string[]) {
  if (data.length === 0) return { missing: 0, score: 0 };
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
