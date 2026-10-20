const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("bios", {
  call: (metodo, rota, corpo) => ipcRenderer.invoke("bios:call", { metodo, rota, corpo }),
  temChave: () => ipcRenderer.invoke("bios:temChave"),
  salvarChave: (k) => ipcRenderer.invoke("bios:salvarChave", k),
  abrirPasta: () => ipcRenderer.invoke("bios:abrirPasta"),
});
