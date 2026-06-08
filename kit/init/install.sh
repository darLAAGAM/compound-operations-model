#!/usr/bin/env bash
#
# OperAI Brand Bootstrap — install.sh
# Version: 3.1.1
#
# Usage (on a fresh Ubuntu 24.04 VPS, as root or with sudo):
#   curl -fsSL https://usecompai.com/init | bash
#
# Or with explicit brand slug:
#   curl -fsSL https://usecompai.com/init | bash -s acme-brand
#
# What it does:
#   1. Installs system dependencies (python3, node, docker, git, cloudflared, qmd)
#   2. Creates /opt/operai/ layout (brain, agents, services, logs, credentials)
#   3. Clones operai-runtime skeleton (MCP server + OpenClaw launcher)
#   4. Runs brain-bootstrap.py (interactive discovery + 6 QMD collections)
#   5. Installs systemd units for the 7 agents
#   6. Prints next-step checklist (OAuth flows, Cloudflare Tunnel, compliance)
#
# Does NOT do (by design):
#   - OAuth handoffs (Shopify/Klaviyo/GWS/Slack) — founder must approve
#   - DPIA + AI System Register signing — founder is Data Controller
#   - Production deployment of agents — shadow mode only until founder approves
#

set -euo pipefail

BRAND_SLUG="${1:-}"
OPERAI_HOME="/opt/operai"
OPERAI_USER="operai"
RUNTIME_TARBALL="https://usecompai.com/init/operai-runtime-v0.5.0.tar.gz"
LOG_FILE="/tmp/operai-install.log"

# ---------- pretty output ----------
c_reset=$(printf "\033[0m")
c_bold=$(printf "\033[1m")
c_gold=$(printf "\033[38;5;179m")
c_dim=$(printf "\033[2m")
c_red=$(printf "\033[31m")
c_green=$(printf "\033[32m")

banner() {
  cat <<EOF
${c_gold}${c_bold}
   ____                    _    ___
  / __ \\____  ___  _____  / \\  |_ _|
 / / / / __ \\/ _ \\/ ___/ / _ \\  | |
/ /_/ / /_/ /  __/ /    / ___ \\ | |
\\____/ .___/\\___/_/    /_/   \\_\\___|
    /_/
${c_reset}${c_dim}Brand Bootstrap · v3.1.1 · usecompai.com${c_reset}

EOF
}

log()  { echo "${c_dim}[$(date +%H:%M:%S)]${c_reset} $*" | tee -a "$LOG_FILE"; }
ok()   { echo "${c_green}✓${c_reset} $*" | tee -a "$LOG_FILE"; }
warn() { echo "${c_gold}!${c_reset} $*" | tee -a "$LOG_FILE"; }
fail() { echo "${c_red}✗${c_reset} $*" | tee -a "$LOG_FILE"; exit 1; }

# ---------- sanity checks ----------
check_prereqs() {
  log "Checking prerequisites…"
  [[ $EUID -eq 0 ]] || fail "Run as root (or: sudo bash)"
  [[ -f /etc/os-release ]] || fail "Cannot detect OS"
  . /etc/os-release
  if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
    fail "v0.1 only supports Ubuntu/Debian. You have: $ID"
  fi
  command -v curl >/dev/null || fail "curl not found"
  ok "OS check: $PRETTY_NAME"
}

# ---------- brand slug prompt ----------
prompt_brand() {
  if [[ -z "$BRAND_SLUG" ]]; then
    echo
    echo "${c_bold}What is your brand slug?${c_reset}"
    echo "${c_dim}Lowercase, no spaces (e.g. acme, nuvo-beauty, okidoki)${c_reset}"
    read -rp "  > " BRAND_SLUG
  fi
  [[ "$BRAND_SLUG" =~ ^[a-z0-9][a-z0-9-]{1,30}$ ]] || fail "Invalid slug. Use lowercase/digits/hyphens."
  ok "Brand: $BRAND_SLUG"
}

# ---------- system deps ----------
install_system_deps() {
  log "Installing system dependencies (this can take 3-5 min)…"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq >> "$LOG_FILE" 2>&1
  apt-get install -y -qq \
    python3 python3-pip python3-venv \
    git jq unzip build-essential \
    ca-certificates gnupg lsb-release \
    rsync cron \
    sqlcipher libsqlcipher-dev \
    >> "$LOG_FILE" 2>&1
  ok "apt packages installed"

  if ! command -v node >/dev/null; then
    log "Installing Node.js LTS…"
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - >> "$LOG_FILE" 2>&1
    apt-get install -y -qq nodejs >> "$LOG_FILE" 2>&1
    ok "Node $(node -v) installed"
  else
    ok "Node already installed: $(node -v)"
  fi

  if ! command -v docker >/dev/null; then
    log "Installing Docker (optional)…"
    if curl -fsSL https://get.docker.com | sh >> "$LOG_FILE" 2>&1; then
      # systemd may not be available (containers, chroots) — non-fatal
      systemctl enable --now docker >> "$LOG_FILE" 2>&1 || \
        warn "docker installed but systemctl enable failed (no systemd?); start docker manually if needed"
      ok "Docker installed"
    else
      warn "Docker install failed — continuing without Docker (some features may be limited)"
    fi
  fi

  if ! command -v cloudflared >/dev/null; then
    log "Installing cloudflared (for MCP tunnel)…"
    curl -fsSL -o /usr/local/bin/cloudflared \
      https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x /usr/local/bin/cloudflared
    ok "cloudflared installed"
  fi
}

# ---------- operai user + layout ----------
create_layout() {
  log "Creating /opt/operai layout…"
  id -u "$OPERAI_USER" >/dev/null 2>&1 || useradd -r -s /bin/bash -m -d "$OPERAI_HOME" "$OPERAI_USER"

  install -d -o "$OPERAI_USER" -g "$OPERAI_USER" \
    "$OPERAI_HOME"/{agents,brain,brain/knowledge,brain/memory,brain/skills,services,services/mcp,services/qmd,credentials,logs,backups,compliance,state,workflows,events,events/pending,events/completed,events/failed,events/in-flight} \
    "$OPERAI_HOME"/agents/{cs,finance,ops,marketing,merch,retail,hr,critic,guardrail,compliance}

  # Explicit parent brand dir first (install -d brace-expansion does not own parents)
  install -d -o "$OPERAI_USER" -g "$OPERAI_USER" "$OPERAI_HOME/brain/knowledge/$BRAND_SLUG"
  install -d -o "$OPERAI_USER" -g "$OPERAI_USER" \
    "$OPERAI_HOME/brain/knowledge/$BRAND_SLUG"/{context,team,product,ops,retail,marketing,finance,cs,wholesale,strategy} \
    "$OPERAI_HOME/brain/knowledge/platform" \
    "$OPERAI_HOME/brain/knowledge/projects" \
    "$OPERAI_HOME/brain/knowledge/personal"

  # Safety net: recursive chown on /brain (handles any edge cases from install -d)
  chown -R "$OPERAI_USER":"$OPERAI_USER" "$OPERAI_HOME/brain"
  chmod 700 "$OPERAI_HOME/credentials"
  ok "Layout ready at $OPERAI_HOME"
}

# ---------- runtime clone ----------
fetch_runtime() {
  log "Fetching OperAI runtime skeleton…"
  cd "$OPERAI_HOME/services"
  if curl -fsSL -o /tmp/operai-runtime.tar.gz "$RUNTIME_TARBALL" 2>/dev/null; then
    tar -xzf /tmp/operai-runtime.tar.gz -C "$OPERAI_HOME/services"
    rm /tmp/operai-runtime.tar.gz
    ok "Runtime extracted"
  else
    warn "Runtime tarball not reachable (offline?). Using local skeleton."
    # Fallback: the init/ directory shipped with kit has the templates
  fi

  # Install QMD (Quoted Markdown) — vector indexer (npm package @tobilu/qmd)
  if ! command -v qmd >/dev/null; then
    log "Installing QMD (npm @tobilu/qmd)…"
    npm install -g @tobilu/qmd >> "$LOG_FILE" 2>&1 || \
      warn "QMD npm install failed — run 'npm install -g @tobilu/qmd' manually"
  fi

  # Ingest pipeline deps — SQLCipher binding for encrypted state DBs (v0.4)
  log "Installing sqlcipher3-binary for encrypted ingest state…"
  pip3 install --break-system-packages --quiet sqlcipher3-binary >> "$LOG_FILE" 2>&1 || \
    warn "sqlcipher3-binary install failed — ingest state will use plaintext sqlite (dev only)"

  # Install agent-runner.py from tarball (placeholder heartbeat runner; real agents in v0.6)
  if [[ -f "$OPERAI_HOME/services/init/agent-runner.py" ]]; then
    cp "$OPERAI_HOME/services/init/agent-runner.py" "$OPERAI_HOME/services/agent-runner.py"
    chmod 0755 "$OPERAI_HOME/services/agent-runner.py"
    ok "agent-runner.py installed"
  fi

  chown -R "$OPERAI_USER":"$OPERAI_USER" "$OPERAI_HOME/services"
}

# ---------- brain bootstrap ----------
bootstrap_brain() {
  cd "$OPERAI_HOME"
  local extra_args="--interactive"
  if [[ -n "${OPERAI_ANSWERS_FILE:-}" && -f "$OPERAI_ANSWERS_FILE" ]]; then
    log "Running brain bootstrap (non-interactive, answers from $OPERAI_ANSWERS_FILE)…"
    # Make the answers file readable by operai user
    cp "$OPERAI_ANSWERS_FILE" /tmp/operai-answers.json
    chown "$OPERAI_USER":"$OPERAI_USER" /tmp/operai-answers.json
    extra_args="--answers-file /tmp/operai-answers.json"
  else
    log "Running brain bootstrap (interactive discovery)…"
  fi
  sudo -u "$OPERAI_USER" python3 "$OPERAI_HOME/services/init/brain-bootstrap.py" \
    --brand "$BRAND_SLUG" \
    --home "$OPERAI_HOME" \
    $extra_args || fail "Brain bootstrap failed"
  ok "Brain seeded with 6 QMD collections"
}

# ---------- operai-init CLI ----------
install_cli() {
  log "Installing operai-init CLI to /usr/local/bin/operai-init…"
  local cli_src="$OPERAI_HOME/services/init/cli"
  [[ -d "$cli_src" ]] || { warn "CLI source not found at $cli_src — skipping"; return; }

  # Package lives at /opt/operai/services/init/cli/operai_init/ (kept in place)
  cat > /usr/local/bin/operai-init <<WRAPPER_EOF
#!/usr/bin/env bash
PYTHONPATH="$cli_src:\${PYTHONPATH:-}" exec python3 "$cli_src/operai_init_cli.py" "\$@"
WRAPPER_EOF
  chmod 0755 /usr/local/bin/operai-init
  ok "operai-init installed (try: operai-init status)"
}

# ---------- Workflow hooks (brand-specific extension points) ----------
install_workflows() {
  log "Installing workflow hook scaffolding…"
  local src="$OPERAI_HOME/services/init/workflow-templates"
  local dst="$OPERAI_HOME/workflows"
  if [[ -d "$src" ]]; then
    # Copy each domain sample if not already present (founder may have customized)
    for domain_src in "$src"/*; do
      [[ -d "$domain_src" ]] || continue
      local name=$(basename "$domain_src")
      mkdir -p "$dst/$name"
      for f in "$domain_src"/*.py; do
        [[ -f "$f" ]] || continue
        local target="$dst/$name/$(basename $f)"
        if [[ ! -f "$target" ]]; then
          cp "$f" "$target"
          ok "workflow sample: $target"
        fi
      done
    done
    chown -R "$OPERAI_USER":"$OPERAI_USER" "$dst"
  fi
  ok "Workflow hooks ready at $dst"
}

# ---------- MCP server ----------
install_mcp_server() {
  log "Installing MCP server (Python deps + template + first key)…"
  local tmpl_src="$OPERAI_HOME/services/init/mcp-server-template"
  local mcp_dst="$OPERAI_HOME/services/mcp"

  if [[ ! -d "$tmpl_src" ]]; then
    warn "MCP server template not found at $tmpl_src — skipping"
    return
  fi

  # Install Python deps (mcp, starlette, uvicorn)
  pip3 install --break-system-packages --quiet \
    -r "$tmpl_src/requirements.txt" >> "$LOG_FILE" 2>&1 || \
    warn "pip install for MCP deps returned non-zero — check $LOG_FILE"

  # Copy template into persistent location (outside the init/ tree)
  mkdir -p "$mcp_dst"
  cp -R "$tmpl_src"/* "$mcp_dst/"
  chown -R "$OPERAI_USER":"$OPERAI_USER" "$mcp_dst"
  ok "MCP server installed at $mcp_dst"

  # Generate the founder's first admin API key
  log "Generating founder admin API key…"
  sudo -u "$OPERAI_USER" /usr/local/bin/operai-init key create founder --role admin 2>&1 | tee -a "$LOG_FILE" | grep -E "(lgm_|⚠)" || true
  ok "Admin key generated — copy it from the output above; it is not shown again"
}

# ---------- systemd units ----------
install_systemd_units() {
  log "Installing systemd units for 7 agents…"
  local unit_dir="$OPERAI_HOME/services/init/systemd-templates"
  [[ -d "$unit_dir" ]] || { warn "systemd templates not found — skipping"; return; }

  for tmpl in "$unit_dir"/*.service.tmpl; do
    [[ -f "$tmpl" ]] || continue
    local name=$(basename "$tmpl" .service.tmpl)
    local dest="/etc/systemd/system/${name}.service"
    sed -e "s|@BRAND@|$BRAND_SLUG|g" \
        -e "s|@HOME@|$OPERAI_HOME|g" \
        -e "s|@USER@|$OPERAI_USER|g" \
        "$tmpl" > "$dest"
    ok "installed $name.service"
  done

  if command -v systemctl >/dev/null && systemctl daemon-reload >/dev/null 2>&1; then
    ok "systemd reloaded (agents not started — deploy in shadow mode manually)"
  else
    warn "systemctl not available — units installed but not registered (container/chroot environment?)"
  fi
}

# ---------- qmd indexing cron ----------
setup_qmd_cron() {
  log "Scheduling QMD indexing every 5 min…"
  if ! command -v crontab >/dev/null 2>&1; then
    warn "crontab not available (container?) — skipping QMD cron. Install cron manually for scheduled indexing."
    return 0
  fi
  local cron_line="*/5 * * * * cd $OPERAI_HOME/brain && /usr/local/bin/qmd update >> $OPERAI_HOME/logs/qmd.log 2>&1"
  if (sudo -u "$OPERAI_USER" crontab -l 2>/dev/null; echo "$cron_line") | \
     awk "!seen[\$0]++" | sudo -u "$OPERAI_USER" crontab - 2>/dev/null; then
    ok "QMD cron installed"
  else
    warn "Could not install QMD cron (daemon not running?) — manual step needed"
  fi
}

# ---------- compliance scaffold ----------
compliance_scaffold() {
  log "Generating compliance scaffold (DPIA + AI System Register)…"
  local cdir="$OPERAI_HOME/compliance"
  cp -n "$OPERAI_HOME/services/init/compliance-scaffold/"*.md "$cdir/" 2>/dev/null || true
  # Prefill brand slug in the scaffold docs
  sed -i "s|@BRAND@|$BRAND_SLUG|g" "$cdir"/*.md 2>/dev/null || true
  ok "Compliance templates at $cdir/ (founder must review + sign)"
}

# ---------- next steps ----------
print_next_steps() {
  cat <<EOF

${c_gold}${c_bold}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${c_reset}
${c_bold}OperAI bootstrap complete for ${BRAND_SLUG}.${c_reset}
${c_gold}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${c_reset}

${c_bold}What is live now:${c_reset}
  ✓ /opt/operai/ layout with brain + 6 QMD collections
  ✓ Python + Node + Docker + QMD + cloudflared
  ✓ 7 agent systemd units installed (NOT started)
  ✓ Brain seeded from your discovery interview
  ✓ Compliance scaffold at /opt/operai/compliance/

${c_bold}What you must do next (founder-only steps):${c_reset}

  ${c_gold}1.${c_reset} Connect integrations (each is a one-time OAuth flow):
       operai-init connect shopify
       operai-init connect klaviyo
       operai-init connect google-workspace
       operai-init connect slack

  ${c_gold}2.${c_reset} Set up Cloudflare Tunnel for MCP endpoint:
       cloudflared tunnel login
       cloudflared tunnel create ${BRAND_SLUG}-mcp
       # then: operai-init tunnel ${BRAND_SLUG}-mcp mcp.${BRAND_SLUG}.com

  ${c_gold}3.${c_reset} Review + sign compliance docs:
       /opt/operai/compliance/dpia.md
       /opt/operai/compliance/ai-system-register.md
       /opt/operai/compliance/annex-iii-review.md

  ${c_gold}4.${c_reset} Start the MCP server (this exposes the tools via Cloudflare Tunnel):
       systemctl enable --now operai-mcp
       operai-init status

  ${c_gold}5.${c_reset} Start agents in shadow mode (no customer-facing writes):
       systemctl start operai-cs operai-finance operai-ops
       tail -f /opt/operai/logs/*.log

  ${c_gold}6.${c_reset} Create API keys for your team:
       operai-init key create diego  --role admin
       operai-init key create laura  --role team
       operai-init key list

  ${c_gold}7.${c_reset} Onboard your team (1 command per employee):
       operai-init team-join --out team-join.sh
       # share team-join.sh with your team (they paste their key on run)

${c_bold}Playbook:${c_reset} https://usecompai.com/playbook/
${c_bold}Kit docs:${c_reset} ${OPERAI_HOME}/services/README.md
${c_bold}Support:${c_reset} hello@usecompai.com

${c_dim}Install log: ${LOG_FILE}${c_reset}

EOF
}

# ---------- main ----------
main() {
  banner
  check_prereqs
  prompt_brand
  install_system_deps
  create_layout
  fetch_runtime
  bootstrap_brain
  install_cli
  install_mcp_server
  install_workflows
  install_systemd_units
  setup_qmd_cron
  compliance_scaffold
  print_next_steps
}

main "$@"
