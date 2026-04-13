export function difficultyBadgeClass(difficulty) {
  if (difficulty === "Easy") return "badge-easy";
  if (difficulty === "Medium") return "badge-medium";
  return "badge-hard";
}

export function toPercent(value) {
  return `${Number(value || 0).toFixed(2)}%`;
}

