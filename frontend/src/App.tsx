import SensorList from "./features/sensors/SensorList";
import { Link, Route, Routes } from "react-router-dom";

const sections = [
  {
    id: "sensors",
    title: "Sensors",
    description: "Monitor temperature, humidity, soil moisture, and more.",
    icon: "🌡️",
  },
  {
    id: "config",
    title: "Configuration",
    description: "Configure greenhouse settings and sensor thresholds.",
    icon: "⚙️",
  },
  {
    id: "automation",
    title: "Automation",
    description: "Manage automatic actions and greenhouse routines.",
    icon: "🤖",
  },
  {
    id: "overview",
    title: "Overview",
    description: "Get a quick overview of your greenhouse status.",
    icon: "📊",
  },
  {
    id: "controls",
    title: "Controls",
    description: "Control greenhouse devices and equipment.",
    icon: "🎛️",
  },
  {
    id: "events",
    title: "Events",
    description: "View system events, alerts, and activity.",
    icon: "🔔",
  },
];

function Dashboard() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <section className="mb-12 text-center">
        <div className="mb-4 text-5xl">🌿</div>

        <h2 className="text-4xl font-bold tracking-tight sm:text-5xl">
          Smart Greenhouse
        </h2>

        <p className="mx-auto mt-4 max-w-2xl text-lg text-slate-400">
          Monitor and control your greenhouse from one place.
        </p>
      </section>

      <section className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {sections.map((section) => (
          <article
            key={section.id}
            id={section.id}
            className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-lg"
          >
            <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800 text-2xl">
              {section.icon}
            </div>

            <h3 className="text-xl font-semibold">{section.title}</h3>

            <p className="mt-2 text-sm leading-6 text-slate-400">
              {section.description}
            </p>

            <Link
              to={`/${section.id}`}
              className="mt-6 block rounded-lg bg-slate-800 px-3 py-2 text-center text-sm text-slate-300 transition hover:bg-slate-700"
            >
              Open
            </Link>
          </article>
        ))}
      </section>
    </main>
  );
}

function SectionPage({
  title,
  description,
  icon,
}: {
  title: string;
  description: string;
  icon: string;
}) {
  return (
    <main className="mx-auto max-w-4xl px-6 py-16">
      <Link
        to="/"
        className="text-sm text-slate-400 transition hover:text-white"
      >
        ← Back to Dashboard
      </Link>

      <div className="mt-10 rounded-2xl border border-slate-800 bg-slate-900 p-8">
        <div className="mb-5 text-5xl">{icon}</div>

        <h2 className="text-3xl font-bold">{title}</h2>

        <p className="mt-3 text-slate-400">{description}</p>

        <div className="mt-8 rounded-lg bg-slate-800 px-4 py-3 text-slate-500">
          Coming soon
        </div>
      </div>
    </main>
  );
}

function SensorsPage() {
  return (
    <main className="mx-auto max-w-7xl px-6 py-16">
      <Link
        to="/"
        className="text-sm text-slate-400 transition hover:text-white"
      >
        ← Back to Dashboard
      </Link>

      <div className="mt-10">
        <div className="mb-8">
          <div className="mb-4 text-5xl">🌡️</div>

          <h2 className="text-3xl font-bold">Sensors</h2>

          <p className="mt-3 text-slate-400">
            Create and monitor greenhouse sensors.
          </p>
        </div>

        <SensorList />
      </div>
    </main>
  );
}

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 bg-slate-900">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-3">
            <span className="text-2xl">🌱</span>

            <div>
              <h1 className="text-lg font-semibold">Smart Greenhouse</h1>
              <p className="text-sm text-slate-400">Home Dashboard</p>
            </div>
          </Link>

          <div className="flex items-center gap-2 rounded-full bg-slate-800 px-3 py-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-green-500" />
            <span className="text-sm text-slate-300">API: OK</span>
          </div>
        </div>
      </header>

      <Routes>
        <Route path="/" element={<Dashboard />} />

        <Route path="/sensors" element={<SensorsPage />} />

        {sections
          .filter((section) => section.id !== "sensors")
          .map((section) => (
            <Route
              key={section.id}
              path={`/${section.id}`}
              element={
                <SectionPage
                  title={section.title}
                  description={section.description}
                  icon={section.icon}
                />
              }
            />
          ))}
      </Routes>
    </div>
  );
}

export default App;