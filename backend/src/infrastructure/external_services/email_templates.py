"""Email templates for different languages."""

EMAIL_TEMPLATES = {
    "en": {
        "register": {
            "subject": "Verify your email address",
            "html": lambda link, hours, name="": f"""
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="color-scheme" content="light">
<title>Verify your email address</title>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<style>
  :root {{
    --brand-primary: #44ba82;
    --brand-dark: #1f2937;
  }}
  body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
  table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
  img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
  body {{ margin: 0; padding: 0; width: 100% !important; height: 100% !important; background-color: #f4f5f7; }}
  a {{ color: #44ba82; }}
  @media screen and (max-width: 600px) {{
    .email-container {{ width: 100% !important; }}
    .px-32 {{ padding-left: 20px !important; padding-right: 20px !important; }}
    .py-40 {{ padding-top: 28px !important; padding-bottom: 28px !important; }}
    h1 {{ font-size: 20px !important; }}
  }}
</style>
</head>
<body style="margin:0; padding:0; background-color:#f4f5f7;">
  <div style="display:none; max-height:0px; max-width:0px; overflow:hidden; mso-hide:all; font-size:1px; line-height:1px; color:#f4f5f7;">
    Click the button to verify your email address. This link expires in {hours} {"hour" if hours == 1 else "hours"}.
  </div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f5f7;">
    <tr>
      <td align="center" style="padding: 32px 16px;">
        <table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px; max-width:600px; background-color:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #e5e7eb;">
          <tr>
            <td align="center" style="background-color:#44ba82; padding:28px 24px;">
              <span style="font-family: Arial, Helvetica, sans-serif; font-size:20px; font-weight:700; color:#ffffff; letter-spacing:0.5px;">
                Gift Planner
              </span>
            </td>
          </tr>
          <tr>
            <td class="px-32 py-40" style="padding: 40px 40px 24px 40px; font-family: Arial, Helvetica, sans-serif;">
              <h1 style="margin:0 0 16px 0; font-size:22px; line-height:28px; color:#1f2937; font-weight:700;">
                Verify your email address
              </h1>
              <p style="margin:0 0 24px 0; font-size:15px; line-height:24px; color:#374151;">
                {"Hello " + name + "," if name else "Hello,"}<br><br>
                Welcome to Gift Planner! Please verify your email address by clicking the button below.
              </p>
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto 28px auto;">
                <tr>
                  <td align="center" style="border-radius:8px; background-color:#44ba82;">
                    <a href="{link}" target="_blank" style="display:inline-block; padding:14px 32px; font-family: Arial, Helvetica, sans-serif; font-size:15px; font-weight:700; color:#ffffff; text-decoration:none; border-radius:8px;">
                      Verify Email
                    </a>
                  </td>
                </tr>
              </table>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#fef3c7; border-radius:8px; margin-bottom:24px;">
                <tr>
                  <td style="padding:12px 16px; font-family: Arial, Helvetica, sans-serif; font-size:13px; line-height:20px; color:#92400e;">
                    ⏱ This link is valid for <strong>{hours} {"hour" if hours == 1 else "hours"}</strong> and can only be used once.
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 8px 0; font-size:13px; line-height:20px; color:#6b7280;">
                If the button doesn't work, copy and paste this link into your browser:
              </p>
              <p style="margin:0 0 24px 0; font-size:13px; line-height:20px; word-break:break-all;">
                <a href="{link}" style="color:#44ba82;">{link}</a>
              </p>
              <p style="margin:0; font-size:13px; line-height:20px; color:#6b7280;">
                If you didn't create an account with Gift Planner, you can safely ignore this email.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 40px;">
              <hr style="border:none; border-top:1px solid #e5e7eb; margin:0;">
            </td>
          </tr>
          <tr>
            <td align="center" style="padding: 24px 40px 32px 40px; font-family: Arial, Helvetica, sans-serif;">
              <p style="margin:0 0 8px 0; font-size:12px; line-height:18px; color:#9ca3af;">
                Need help? Contact us at
                <a href="mailto:support@giftplanner.com" style="color:#9ca3af; text-decoration:underline;">support@giftplanner.com</a>
              </p>
              <p style="margin:0; font-size:12px; line-height:18px; color:#9ca3af;">
                © 2026 Gift Planner. All rights reserved.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
            """,
            "text": lambda link, hours, name="": f"{'Hello ' + name + ',' if name else 'Hello,'}\n\nWelcome to Gift Planner! Please verify your email address by clicking the link below:\n\n{link}\n\nThis link expires in {hours} {'hour' if hours == 1 else 'hours'}.\n\nIf you didn't create an account with Gift Planner, you can safely ignore this email.",
        },
        "reset_password": {
            "subject": "Reset your password",
            "html": lambda link, minutes, name="": f"""
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="color-scheme" content="light">
<title>Reset your password</title>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<style>
  :root {{
    --brand-primary: #44ba82;
    --brand-dark: #1f2937;
  }}
  body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
  table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
  img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
  body {{ margin: 0; padding: 0; width: 100% !important; height: 100% !important; background-color: #f4f5f7; }}
  a {{ color: #44ba82; }}
  @media screen and (max-width: 600px) {{
    .email-container {{ width: 100% !important; }}
    .px-32 {{ padding-left: 20px !important; padding-right: 20px !important; }}
    .py-40 {{ padding-top: 28px !important; padding-bottom: 28px !important; }}
    h1 {{ font-size: 20px !important; }}
  }}
</style>
</head>
<body style="margin:0; padding:0; background-color:#f4f5f7;">
  <div style="display:none; max-height:0px; max-width:0px; overflow:hidden; mso-hide:all; font-size:1px; line-height:1px; color:#f4f5f7;">
    Click the button to create a new password. This link expires in {minutes} minutes.
  </div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f5f7;">
    <tr>
      <td align="center" style="padding: 32px 16px;">
        <table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px; max-width:600px; background-color:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #e5e7eb;">
          <tr>
            <td align="center" style="background-color:#44ba82; padding:28px 24px;">
              <span style="font-family: Arial, Helvetica, sans-serif; font-size:20px; font-weight:700; color:#ffffff; letter-spacing:0.5px;">
                Gift Planner
              </span>
            </td>
          </tr>
          <tr>
            <td class="px-32 py-40" style="padding: 40px 40px 24px 40px; font-family: Arial, Helvetica, sans-serif;">
              <h1 style="margin:0 0 16px 0; font-size:22px; line-height:28px; color:#1f2937; font-weight:700;">
                Reset your password
              </h1>
              <p style="margin:0 0 24px 0; font-size:15px; line-height:24px; color:#374151;">
                {"Hello " + name + "," if name else "Hello,"}<br><br>
                You requested to reset your password for your Gift Planner account. Click the button below to choose a new one.
              </p>
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto 28px auto;">
                <tr>
                  <td align="center" style="border-radius:8px; background-color:#44ba82;">
                    <a href="{link}" target="_blank" style="display:inline-block; padding:14px 32px; font-family: Arial, Helvetica, sans-serif; font-size:15px; font-weight:700; color:#ffffff; text-decoration:none; border-radius:8px;">
                      Reset my password
                    </a>
                  </td>
                </tr>
              </table>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#fef3c7; border-radius:8px; margin-bottom:24px;">
                <tr>
                  <td style="padding:12px 16px; font-family: Arial, Helvetica, sans-serif; font-size:13px; line-height:20px; color:#92400e;">
                    ⏱ This link is valid for <strong>{minutes} minutes</strong> and can only be used once.
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 8px 0; font-size:13px; line-height:20px; color:#6b7280;">
                If the button doesn't work, copy and paste this link into your browser:
              </p>
              <p style="margin:0 0 24px 0; font-size:13px; line-height:20px; word-break:break-all;">
                <a href="{link}" style="color:#44ba82;">{link}</a>
              </p>
              <p style="margin:0; font-size:13px; line-height:20px; color:#6b7280;">
                Didn't request this password reset? You can safely ignore this email: your password will remain unchanged.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 40px;">
              <hr style="border:none; border-top:1px solid #e5e7eb; margin:0;">
            </td>
          </tr>
          <tr>
            <td align="center" style="padding: 24px 40px 32px 40px; font-family: Arial, Helvetica, sans-serif;">
              <p style="margin:0 0 8px 0; font-size:12px; line-height:18px; color:#9ca3af;">
                Need help? Contact us at
                <a href="mailto:support@giftplanner.com" style="color:#9ca3af; text-decoration:underline;">support@giftplanner.com</a>
              </p>
              <p style="margin:0; font-size:12px; line-height:18px; color:#9ca3af;">
                © 2026 Gift Planner. All rights reserved.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
            """,
            "text": lambda link, minutes, name="": f"{'Hello ' + name + ',' if name else 'Hello,'}\n\nYou requested to reset your password for your Gift Planner account. Click the link below to choose a new one:\n\n{link}\n\nThis link expires in {minutes} minutes.\n\nDidn't request this password reset? You can safely ignore this email: your password will remain unchanged.",
        },
    },
    "fr": {
        "register": {
            "subject": "Vérifiez votre adresse e-mail",
            "html": lambda link, hours, name="": f"""
<!DOCTYPE html>
<html lang="fr" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="color-scheme" content="light">
<title>Vérifiez votre adresse e-mail</title>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<style>
  :root {{
    --brand-primary: #44ba82;
    --brand-dark: #1f2937;
  }}
  body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
  table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
  img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
  body {{ margin: 0; padding: 0; width: 100% !important; height: 100% !important; background-color: #f4f5f7; }}
  a {{ color: #44ba82; }}
  @media screen and (max-width: 600px) {{
    .email-container {{ width: 100% !important; }}
    .px-32 {{ padding-left: 20px !important; padding-right: 20px !important; }}
    .py-40 {{ padding-top: 28px !important; padding-bottom: 28px !important; }}
    h1 {{ font-size: 20px !important; }}
  }}
</style>
</head>
<body style="margin:0; padding:0; background-color:#f4f5f7;">
  <div style="display:none; max-height:0px; max-width:0px; overflow:hidden; mso-hide:all; font-size:1px; line-height:1px; color:#f4f5f7;">
    Cliquez sur le bouton pour vérifier votre adresse e-mail. Ce lien expire dans {hours} {"heure" if hours == 1 else "heures"}.
  </div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f5f7;">
    <tr>
      <td align="center" style="padding: 32px 16px;">
        <table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px; max-width:600px; background-color:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #e5e7eb;">
          <tr>
            <td align="center" style="background-color:#44ba82; padding:28px 24px;">
              <span style="font-family: Arial, Helvetica, sans-serif; font-size:20px; font-weight:700; color:#ffffff; letter-spacing:0.5px;">
                Gift Planner
              </span>
            </td>
          </tr>
          <tr>
            <td class="px-32 py-40" style="padding: 40px 40px 24px 40px; font-family: Arial, Helvetica, sans-serif;">
              <h1 style="margin:0 0 16px 0; font-size:22px; line-height:28px; color:#1f2937; font-weight:700;">
                Vérifiez votre adresse e-mail
              </h1>
              <p style="margin:0 0 24px 0; font-size:15px; line-height:24px; color:#374151;">
                {"Bonjour " + name + "," if name else "Bonjour,"}<br><br>
                Bienvenue sur Gift Planner ! Veuillez vérifier votre adresse e-mail en cliquant sur le bouton ci-dessous.
              </p>
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto 28px auto;">
                <tr>
                  <td align="center" style="border-radius:8px; background-color:#44ba82;">
                    <a href="{link}" target="_blank" style="display:inline-block; padding:14px 32px; font-family: Arial, Helvetica, sans-serif; font-size:15px; font-weight:700; color:#ffffff; text-decoration:none; border-radius:8px;">
                      Vérifier l'e-mail
                    </a>
                  </td>
                </tr>
              </table>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#fef3c7; border-radius:8px; margin-bottom:24px;">
                <tr>
                  <td style="padding:12px 16px; font-family: Arial, Helvetica, sans-serif; font-size:13px; line-height:20px; color:#92400e;">
                    ⏱ Ce lien est valable <strong>{hours} {"heure" if hours == 1 else "heures"}</strong> et ne peut être utilisé qu'une seule fois.
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 8px 0; font-size:13px; line-height:20px; color:#6b7280;">
                Si le bouton ne fonctionne pas, copiez-collez ce lien dans votre navigateur :
              </p>
              <p style="margin:0 0 24px 0; font-size:13px; line-height:20px; word-break:break-all;">
                <a href="{link}" style="color:#44ba82;">{link}</a>
              </p>
              <p style="margin:0; font-size:13px; line-height:20px; color:#6b7280;">
                Si vous n'avez pas créé de compte sur Gift Planner, vous pouvez ignorer cet e-mail en toute sécurité.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 40px;">
              <hr style="border:none; border-top:1px solid #e5e7eb; margin:0;">
            </td>
          </tr>
          <tr>
            <td align="center" style="padding: 24px 40px 32px 40px; font-family: Arial, Helvetica, sans-serif;">
              <p style="margin:0 0 8px 0; font-size:12px; line-height:18px; color:#9ca3af;">
                Besoin d'aide ? Contactez-nous à
                <a href="mailto:support@giftplanner.com" style="color:#9ca3af; text-decoration:underline;">support@giftplanner.com</a>
              </p>
              <p style="margin:0; font-size:12px; line-height:18px; color:#9ca3af;">
                © 2026 Gift Planner. Tous droits réservés.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
            """,
            "text": lambda link, hours, name="": f"{'Bonjour ' + name + ',' if name else 'Bonjour,'}\n\nBienvenue sur Gift Planner ! Veuillez vérifier votre adresse e-mail en cliquant sur le lien ci-dessous :\n\n{link}\n\nCe lien expire dans {hours} {'heure' if hours == 1 else 'heures'}.\n\nSi vous n'avez pas créé de compte sur Gift Planner, vous pouvez ignorer cet e-mail en toute sécurité.",
        },
        "reset_password": {
            "subject": "Réinitialisez votre mot de passe",
            "html": lambda link, minutes, name="": f"""
<!DOCTYPE html>
<html lang="fr" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="color-scheme" content="light">
<title>Réinitialisation de votre mot de passe</title>
<!--[if mso]>
<noscript>
<xml>
<o:OfficeDocumentSettings>
<o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings>
</xml>
</noscript>
<![endif]-->
<style>
  :root {{
    --brand-primary: #44ba82;
    --brand-dark: #1f2937;
  }}
  body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
  table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
  img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }}
  body {{ margin: 0; padding: 0; width: 100% !important; height: 100% !important; background-color: #f4f5f7; }}
  a {{ color: #44ba82; }}
  @media screen and (max-width: 600px) {{
    .email-container {{ width: 100% !important; }}
    .px-32 {{ padding-left: 20px !important; padding-right: 20px !important; }}
    .py-40 {{ padding-top: 28px !important; padding-bottom: 28px !important; }}
    h1 {{ font-size: 20px !important; }}
  }}
</style>
</head>
<body style="margin:0; padding:0; background-color:#f4f5f7;">
  <div style="display:none; max-height:0px; max-width:0px; overflow:hidden; mso-hide:all; font-size:1px; line-height:1px; color:#f4f5f7;">
    Cliquez sur le bouton pour créer un nouveau mot de passe. Ce lien expire dans {minutes} minutes.
  </div>
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f5f7;">
    <tr>
      <td align="center" style="padding: 32px 16px;">
        <table role="presentation" class="email-container" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px; max-width:600px; background-color:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #e5e7eb;">
          <tr>
            <td align="center" style="background-color:#44ba82; padding:28px 24px;">
              <span style="font-family: Arial, Helvetica, sans-serif; font-size:20px; font-weight:700; color:#ffffff; letter-spacing:0.5px;">
                Gift Planner
              </span>
            </td>
          </tr>
          <tr>
            <td class="px-32 py-40" style="padding: 40px 40px 24px 40px; font-family: Arial, Helvetica, sans-serif;">
              <h1 style="margin:0 0 16px 0; font-size:22px; line-height:28px; color:#1f2937; font-weight:700;">
                Réinitialisation de votre mot de passe
              </h1>
              <p style="margin:0 0 24px 0; font-size:15px; line-height:24px; color:#374151;">
                {"Bonjour " + name + "," if name else "Bonjour,"}<br><br>
                Vous avez demandé à réinitialiser le mot de passe de votre compte Gift Planner. Cliquez sur le bouton ci-dessous pour en choisir un nouveau.
              </p>
              <table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin: 0 auto 28px auto;">
                <tr>
                  <td align="center" style="border-radius:8px; background-color:#44ba82;">
                    <a href="{link}" target="_blank" style="display:inline-block; padding:14px 32px; font-family: Arial, Helvetica, sans-serif; font-size:15px; font-weight:700; color:#ffffff; text-decoration:none; border-radius:8px;">
                      Réinitialiser mon mot de passe
                    </a>
                  </td>
                </tr>
              </table>
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#fef3c7; border-radius:8px; margin-bottom:24px;">
                <tr>
                  <td style="padding:12px 16px; font-family: Arial, Helvetica, sans-serif; font-size:13px; line-height:20px; color:#92400e;">
                    ⏱ Ce lien est valable <strong>{minutes} minutes</strong> et ne peut être utilisé qu'une seule fois.
                  </td>
                </tr>
              </table>
              <p style="margin:0 0 8px 0; font-size:13px; line-height:20px; color:#6b7280;">
                Si le bouton ne fonctionne pas, copiez-collez ce lien dans votre navigateur :
              </p>
              <p style="margin:0 0 24px 0; font-size:13px; line-height:20px; word-break:break-all;">
                <a href="{link}" style="color:#44ba82;">{link}</a>
              </p>
              <p style="margin:0; font-size:13px; line-height:20px; color:#6b7280;">
                Vous n'êtes pas à l'origine de cette demande ? Vous pouvez ignorer cet e-mail en toute sécurité : votre mot de passe restera inchangé.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding: 0 40px;">
              <hr style="border:none; border-top:1px solid #e5e7eb; margin:0;">
            </td>
          </tr>
          <tr>
            <td align="center" style="padding: 24px 40px 32px 40px; font-family: Arial, Helvetica, sans-serif;">
              <p style="margin:0 0 8px 0; font-size:12px; line-height:18px; color:#9ca3af;">
                Besoin d'aide ? Contactez-nous à
                <a href="mailto:support@giftplanner.com" style="color:#9ca3af; text-decoration:underline;">support@giftplanner.com</a>
              </p>
              <p style="margin:0; font-size:12px; line-height:18px; color:#9ca3af;">
                © 2026 Gift Planner. Tous droits réservés.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
            """,
            "text": lambda link, minutes, name="": f"{'Bonjour ' + name + ',' if name else 'Bonjour,'}\n\nVous avez demandé à réinitialiser le mot de passe de votre compte Gift Planner. Cliquez sur le lien ci-dessous pour en choisir un nouveau :\n\n{link}\n\nCe lien expire dans {minutes} minutes.\n\nVous n'êtes pas à l'origine de cette demande ? Vous pouvez ignorer cet e-mail en toute sécurité : votre mot de passe restera inchangé.",
        },
    },
}


def get_email_template(template_type: str, locale: str = "en"):
    """Get email template for specific type and locale.
    
    Args:
        template_type: Type of template ('register' or 'reset_password')
        locale: Language locale ('en' or 'fr')
    
    Returns:
        Dictionary with subject, html, and text template functions
    """
    if locale not in EMAIL_TEMPLATES:
        locale = "en"
    
    if template_type not in EMAIL_TEMPLATES[locale]:
        # Fallback to English if template type not found
        locale = "en"
    
    return EMAIL_TEMPLATES[locale][template_type]
