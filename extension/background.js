// Mengizinkan user membuka panel samping (Side Panel) dengan mengklik ikon ekstensi
chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error(error));
