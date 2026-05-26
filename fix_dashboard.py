
html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>لوحة الطالب | أكاديمية التقدم</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="stylesheet" href="{{ url_for('static', filename='css/student_dashboard.css') }}">
</head>
<body class="student-page">

  <!-- شريط علوي + هيرو -->
  <header class="student-hero">

    <!-- الخلفية مع الطبقة الزرقاء -->
    <div class="student-hero-bg">
      <img src="{{ url_for('static', filename='assets/book.jpg') }}" alt="خلفية طالب يقرأ" class="student-hero-image">
      <div class="student-hero-overlay"></div>
    </div>

    <!-- النافبار -->
    <nav class="student-navbar">
      <!-- الروابط (يمين) -->
      <ul class="student-nav-links">
        <li><a href="#" class="nav-link active">الرئيسية</a></li>
        <li><a href="#schedule" class="nav-link">الجدول الدراسي</a></li>
        <li><a href="#attendance" class="nav-link">الحضور والغياب</a></li>
        <li><a href="#points" class="nav-link">نقاطك</a></li>
        <li><a href="#events" class="nav-link">الفعاليات</a></li>
        <li><a href="{{ url_for('logout') }}" class="nav-link nav-logout">تسجيل الخروج</a></li>
      </ul>

      <!-- الشعار (يسار) -->
      <div class="student-logo">
        <img src="{{ url_for('static', filename='assets/logoAA-removebg-preview.png') }}" alt="أكاديمية التقدم">
      </div>
    </nav>

    <!-- محتوى الترحيب فوق الصورة -->
    <div class="student-hero-content">
      <p class="student-welcome">
        مرحباً بك، <span>{{ student_name or 'student2025' }}</span>
      </p>
      <h1 class="student-hero-title">لوحة الطالب</h1>
      <p class="student-hero-subtitle">
        هنا يمكنك متابعة جدولك الدراسي، حضورك وغيابك، ونقاطك الأسبوعية في الأكاديمية.
      </p>
    </div>
  </header>

  <!-- هنا تبدأ باقي محتويات لوحة الطالب (الكروت، الجداول، الرسوم البيانية...) -->
  <main class="student-main">

      <!-- صف 1 : كرت النقاط -->
      <section class="grid-row" id="points">
        <!-- كرت النقاط -->
        <article class="card points-card">
          <div class="card-header">
            <h2>نقاطك هذا الأسبوع</h2>
            <span class="badge badge-green">مستوى مميز</span>
          </div>

          <div class="points-main">
            <div class="points-total">
              <span class="points-number">120</span>
              <span class="points-label">إجمالي النقاط</span>
            </div>

            <ul class="points-list">
              <li>
                <span>اللغة الإنجليزية</span>
                <span class="pill">+20</span>
              </li>
              <li>
                <span>الرياضيات</span>
                <span class="pill">+15</span>
              </li>
              <li>
                <span>الالتزام والحضور</span>
                <span class="pill">+10</span>
              </li>
            </ul>
          </div>
        </article>
      </section>

      <!-- صف 2 : جدول اليوم + التنبيهات -->
      <section class="grid-row" id="schedule">
        <!-- جدول اليوم -->
        <article class="card schedule-card">
          <div class="card-header">
            <h2>حصص اليوم</h2>
            <span class="badge">الأربعاء  /  10:00 ص</span>
          </div>

          <table class="schedule-table">
            <thead>
              <tr>
                <th>الحصة</th>
                <th>المادة</th>
                <th>المعلم</th>
                <th>الصف / القاعة</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>الأولى</td>
                <td>اللغة الإنجليزية</td>
                <td>أ. خالد المطيري</td>
                <td>1A بنين</td>
              </tr>
              <tr>
                <td>الثانية</td>
                <td>الرياضيات</td>
                <td>أ. نايف العتيبي</td>
                <td>1A بنين</td>
              </tr>
              <tr>
                <td>الثالثة</td>
                <td>مهارات رقمية</td>
                <td>أ. عبدالله الشهري</td>
                <td>معمل الحاسب</td>
              </tr>
            </tbody>
          </table>
        </article>

        <!-- التنبيهات -->
        <article class="card notices-card">
          <div class="card-header">
            <h2>آخر التنبيهات</h2>
          </div>

          <ul class="notice-list">
            <li>
              <span class="notice-title">اختبار قصير في مادة الرياضيات غداً.</span>
              <span class="notice-meta">من أ. نايف · منذ 3 ساعات</span>
            </li>
            <li>
              <span class="notice-title">تسليم واجب اللغة الإنجليزية قبل يوم الأحد.</span>
              <span class="notice-meta">من أ. خالد · أمس</span>
            </li>
            <li>
              <span class="notice-title">تهانينا! تم اختيارك من الطلاب المتميزين هذا الأسبوع.</span>
              <span class="notice-meta">من إدارة الأكاديمية · هذا الأسبوع</span>
            </li>
          </ul>
        </article>
      </section>

      <!-- قسم من نحن - About Advantage Academy -->
      <section class="about-academy" id="about">
        <div class="about-inner">
          <!-- عنوان رئيسي -->
          <header class="about-header">
            <span class="about-eyebrow">من نحن</span>
            <h2 class="about-title">أكاديمية التقدّم – Advantage Academy</h2>
            <p class="about-lead">
              أكاديمية تعليمية غير ربحية مدعومة من أرامكو السعودية، تُقدِّم برامج نوعية في
              اللغة الإنجليزية والرياضيات لليتامى والطلاب المحتاجين، في بيئة تعليمية آمنة
              ومحفِّزة تفتح لهم أبواب المستقبل.
            </p>
          </header>

          <!-- شبكة المحتوى -->
          <div class="about-grid">
            <!-- العمود الأيمن: نص تعريفي -->
            <div class="about-column about-text">
              <h3>ماذا نقدّم للطلاب؟</h3>
              <ul class="about-list">
                <li>
                  🧠 <strong>تعليم أكاديمي مركّز</strong> في مهارات اللغة الإنجليزية
                  والرياضيات، مع خطط دراسية مصمَّمة لتقوية الأساس وبناء الثقة.
                </li>
                <li>
                  🎯 <strong>متابعة فردية لكل طالب</strong> عبر نقاط أسبوعية، حضور وغياب،
                  وتقارير أداء تساعد الطالب وولي الأمر على معرفة مستوى التقدّم.
                </li>
                <li>
                  🌱 <strong>دعم نفسي واجتماعي</strong> من خلال فعاليات وأنشطة تبني
                  الشخصية، وتغرس قيمة المسؤولية، وروح التعاون والانتماء.
                </li>
                <li>
                  🚀 <strong>تهيئة للمرحلة الجامعية وسوق العمل</strong> عبر مهارات حياتية،
                  واتصال حقيقي برؤية المملكة 2030 وفرص المستقبل.
                </li>
              </ul>
            </div>

            <!-- العمود الأيسر: أرقام وإحصائيات -->
            <div class="about-column about-stats">
              <h3>أثر الأكاديمية</h3>
              <div class="stats-row">
                <div class="stat-card">
                  <span class="stat-number">+250</span>
                  <span class="stat-label">طالب وطالبة مدعومين</span>
                </div>
                <div class="stat-card">
                  <span class="stat-number">+30</span>
                  <span class="stat-label">معلم ومعلمة متطوعين ومختصين</span>
                </div>
                <div class="stat-card">
                  <span class="stat-number">100%</span>
                  <span class="stat-label">برامج مجانية لليتامى والمحتاجين</span>
                </div>
              </div>

              <div class="about-pill">
                <p>
                  في Advantage Academy نؤمن أن <strong>فرصة تعليم حقيقية</strong> يمكن أن
                  تغيّر حياة طالب، وأسرة كاملة، ومستقبل مجتمع كامل.
                </p>
              </div>
            </div>
          </div>

          <!-- قيم الأكاديمية -->
          <section class="about-values">
            <h3>قيمنا في الأكاديمية</h3>
            <div class="values-row">
              <div class="value-card">
                <h4>التعلّم للجميع</h4>
                <p>
                  نوفّر تعليماً نوعياً مجانياً لليتامى والطلاب المحتاجين بدون أي حواجز
                  مادية، ليشعر كل طالب أن له مقعداً ثابتاً وفرصة عادلة.
                </p>
              </div>
              <div class="value-card">
                <h4>رعاية متكاملة</h4>
                <p>
                  نهتم بالجانب الأكاديمي، والنفسي، والاجتماعي، لنساعد الطالب على النمو
                  كإنسان متوازن قبل أن يكون متفوقاً دراسياً.
                </p>
              </div>
              <div class="value-card">
                <h4>شراكات مجتمعية</h4>
                <p>
                  نتعاون مع أرامكو السعودية وجهات خيرية وشركاء تعليم؛ لنصنع معاً رحلة
                  تعليمية مستدامة تأخذ الطالب من مقاعد الدراسة إلى أبواب المستقبل.
                </p>
              </div>
            </div>
          </section>
        </div>
      </section>

  </main>

</body>
</html>
"""

with open(r"c:\Users\manxs\OneDrive\سطح المكتب\advantage_portal\templates\student_dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_content)
