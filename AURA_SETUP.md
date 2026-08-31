# 🔌 Neo4j Aura Setup — do this BEFORE Session 3 (takes ~3 minutes)

Session 3 uses **Neo4j Aura Free** — a free, cloud-hosted Neo4j instance. No credit card, no installation, no Docker. You need exactly three things at the start of the session: a **URI**, a **username**, and a **password**. This guide gets you all three.

## Steps

1. **Create an account** — go to <https://console.neo4j.io> and sign up (Google/email SSO works). Choose the free tier if asked about plans.

2. **Create an instance** — in the console, click **Create instance** (or "New Instance"). Pick:
   - Type: **AuraDB Free**
   - Region: anything close to you (Tokyo/Singapore for JP participants, Frankfurt/Paris for EU)
   - Name: `nordwind` (or anything you like)

3. **⚠️ SAVE YOUR CREDENTIALS — this is the step people miss.** Immediately after creation, Aura shows the generated password **once** and offers a **"Download and continue"** button that saves a `.txt` file containing your URI, username, and password. **Download it.** If you skip this, you cannot see the password again (you'd have to reset it from the instance's ••• menu — not a disaster, but avoidable).

4. **Wait for the instance to start** — the status badge goes from "Creating" to **"Running"** in 1–2 minutes.

5. **Verify** — open the credentials `.txt`. You should see something like:
   ```
   NEO4J_URI=neo4j+s://a1b2c3d4.databases.neo4j.io
   NEO4J_USERNAME=a1b2c3d4
   NEO4J_PASSWORD=xxxxxxxxxxxxxxxxxxxx
   ```
   Those three values (URI, **username**, password) are what you'll paste into the Session 3 notebook and the Graph Navigator. Done. ✅

   > ⚠️ **The username is NOT `neo4j` on current Aura instances** — it's the instance id (the same 8 characters as in the URI). Copy it from the file. Using `neo4j` fails with "Invalid credential" even when the password is right.

## Good to know

- **Free tier limits:** 1 instance, 200k nodes / 400k relationships — our workshop graph is 73 nodes, so we use 0.04% of it. 😄
- **Instances pause after 3 days of inactivity.** If yours is paused on session day, just press **Resume** in the console (~1 minute). If you created it more than 3 days before the session, check this the morning of.
- **Keep the password out of git/screenshots.** It's a real database on the public internet.
- The console's **Query** tab is a full Neo4j Browser — we'll use it during the session to see the graph rendered live from the database, so keep the console tab open.

## Troubleshooting

- *"Connection refused / ServiceUnavailable" in the notebook* → instance is paused (Resume it) or the URI was mistyped — it must start with `neo4j+s://`.
- *"Authentication failure" / "Invalid credential"* → **first check the username**: it must be the `NEO4J_USERNAME` from your file (the instance id), not `neo4j`. If that's right, it's a password typo; reset it via the instance ••• menu → "Reset password", download the new file.
- *Corporate network blocks it* → Aura uses port 7687 (bolt over TLS); try a hotspot if your office firewall is aggressive.
- *No account possible at all* → come anyway: the visual half of the session needs no database, and you can pair with a neighbor for the query cells.
