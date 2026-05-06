Name:           startup-manager
Version:        1.0
Release:        1%{?dist}
Summary:        Gerenciador de atraso para inicialização de apps
License:        MIT
BuildArch:      noarch
Source0:        startup-manager-1.0.tar.gz

Requires:       python3
Requires:       python3-pyqt6

%description
Um utilitário para organizar a inicialização de aplicativos com delay no Fedora KDE.

%prep
%setup -q -c

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/startup-manager
mkdir -p %{buildroot}%{_datadir}/applications

# Criando as pastas para cada resolução
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/

# Instalando scripts e desktop
install -m 755 main.py %{buildroot}%{_datadir}/startup-manager/main.py
install -m 755 logic.py %{buildroot}%{_datadir}/startup-manager/logic.py
install -m 644 startup-manager.desktop %{buildroot}%{_datadir}/applications/startup-manager.desktop

# Instalando os ícones (todos com o mesmo nome final para o sistema mapear)
install -m 644 icon_48.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/startup-manager-icon.png
install -m 644 icon_128.png %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/startup-manager-icon.png
install -m 644 icon_256.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/startup-manager-icon.png

ln -s %{_datadir}/startup-manager/main.py %{buildroot}%{_bindir}/startup-manager

%files
%{_bindir}/startup-manager
%{_datadir}/startup-manager/main.py
%{_datadir}/startup-manager/logic.py
%{_datadir}/applications/startup-manager.desktop
# Registrando todos os caminhos de ícones
%{_datadir}/icons/hicolor/48x48/apps/startup-manager-icon.png
%{_datadir}/icons/hicolor/128x128/apps/startup-manager-icon.png
%{_datadir}/icons/hicolor/256x256/apps/startup-manager-icon.png

%changelog
* Tue May 05 2026 Luis <seuemail@email.com> - 1.0-1
- Adicionado suporte a múltiplas resoluções de ícones (48px, 128px, 256px).
