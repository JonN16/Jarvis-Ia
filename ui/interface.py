"""
UI module - Modern interface for Jarvis
"""

import customtkinter as ctk


class JarvisInterface:
    """Modern Jarvis UI"""

    def __init__(self):
        ctk.set_appearance_mode("dark")
        self.janela = ctk.CTk()
        self.janela.geometry("600x400")
        self.janela.title("Jarvis AI Assistant")
        self.janela.resizable(False, False)

        # Main label
        self.titulo = ctk.CTkLabel(
            self.janela,
            text="Jarvis Online",
            font=("Arial", 32, "bold"),
            text_color="#00BFFF"
        )
        self.titulo.pack(pady=30)

        # Status label
        self.status = ctk.CTkLabel(
            self.janela,
            text="Pronto para receber comandos",
            font=("Arial", 14),
            text_color="#90EE90"
        )
        self.status.pack(pady=10)

        # Command display
        self.comando_label = ctk.CTkLabel(
            self.janela,
            text="",
            font=("Arial", 12),
            text_color="#FFFFFF"
        )
        self.comando_label.pack(pady=20, padx=20, fill="both", expand=True)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.janela, fg_color="transparent")
        buttons_frame.pack(pady=20)

        start_btn = ctk.CTkButton(
            buttons_frame,
            text="Iniciar",
            command=self.on_start,
            fg_color="#00BFFF",
            hover_color="#0099CC"
        )
        start_btn.pack(side="left", padx=10)

        stop_btn = ctk.CTkButton(
            buttons_frame,
            text="Parar",
            command=self.on_stop,
            fg_color="#FF6347",
            hover_color="#FF4500"
        )
        stop_btn.pack(side="left", padx=10)

    def on_start(self):
        """Start listening"""
        self.status.configure(text="Ouvindo...")

    def on_stop(self):
        """Stop listening"""
        self.status.configure(text="Parado")

    def atualizar_status(self, texto):
        """Update status display"""
        self.status.configure(text=texto)

    def atualizar_comando(self, comando):
        """Update command display"""
        self.comando_label.configure(text=f"Comando: {comando}")

    def rodar(self):
        """Run the interface"""
        self.janela.mainloop()

    def fechar(self):
        """Close the interface"""
        self.janela.destroy()


def criar_interface():
    """Create and return the interface instance"""
    return JarvisInterface()
