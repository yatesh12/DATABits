"use client"
import "./Features.css"
import { motion } from "framer-motion"
import { RefreshCw, Cpu, Shield, Database, BarChart, ArrowRight, Zap, Lock } from "lucide-react"
import SectionI from "../Section-I.tsx"

const featuresData = [
  {
    icon: <RefreshCw className="feature-icon" />,
    title: "Real-Time Processing",
    description:
      "Process and transform data streams in real-time with sub-millisecond latency and enterprise-grade reliability.",
    highlight: "Enterprise Ready",
    stats: "99.9% Uptime",
  },
  {
    icon: <Cpu className="feature-icon" />,
    title: "AI-Powered Automation",
    description:
      "Intelligent preprocessing with machine learning algorithms that adapt and optimize based on your data patterns.",
    highlight: "Smart Technology",
    stats: "10x Faster",
  },
  {
    icon: <Shield className="feature-icon" />,
    title: "Enterprise Security",
    description:
      "Bank-grade encryption, SOC 2 compliance, and zero-trust architecture to protect your most sensitive data.",
    highlight: "SOC 2 Certified",
    stats: "Zero Breaches",
  },
  {
    icon: <Database className="feature-icon" />,
    title: "Infinite Scale",
    description:
      "Handle petabytes of data with our distributed cloud infrastructure that scales automatically with demand.",
    highlight: "Auto-Scaling",
    stats: "Petabyte Ready",
  },
  {
    icon: <BarChart className="feature-icon" />,
    title: "Advanced Analytics",
    description:
      "Comprehensive insights with real-time dashboards, custom metrics, and predictive analytics capabilities.",
    highlight: "Real-Time Insights",
    stats: "Live Monitoring",
  },
  {
    icon: <Zap className="feature-icon" />,
    title: "Lightning Fast",
    description: "Optimized performance with edge computing and intelligent caching for instant data transformation.",
    highlight: "Edge Computing",
    stats: "<100ms Response",
  },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
}

const cardVariants = {
  hidden: {
    opacity: 0,
    y: 30,
    scale: 0.95,
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut",
    },
  },
}

export default function Features() {
  return (
    <section className="features">
      {/* Background Elements */}
      <div className="features-background">
        <div className="gradient-orb gradient-orb-1"></div>
        <div className="gradient-orb gradient-orb-2"></div>
        <div className="grid-pattern"></div>
      </div>

      <div className="features-container">
        {/* Header Section */}
        <motion.div
          className="features-header"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <h2 className="features-heading">
            Built for the
            <span className="gradient-text"> Modern Enterprise</span>
          </h2>

          <p className="features-subheading">
            Transform your data infrastructure with enterprise-grade tools designed for scale, security, and
            performance. Join industry leaders who trust our platform.
          </p>

          <div className="features-stats">
            <div className="stat-item">
              <div className="stat-number">10M+</div>
              <div className="stat-label">Records Processed</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number">99.9%</div>
              <div className="stat-label">Uptime SLA</div>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <div className="stat-number">150+</div>
              <div className="stat-label">Integrations</div>
            </div>
          </div>
        </motion.div>

        {/* Feature Cards Grid */}
        <section className="features-II">
        <motion.div className="feature-cards" variants={containerVariants} initial="hidden" animate="visible">
          {featuresData.map((feature, idx) => (
            <motion.div
              key={idx}
              variants={cardVariants}
              whileHover={{
                y: -8,
                transition: { duration: 0.3, ease: "easeOut" },
              }}
              className="feature-card"
            >
              <div className="card-header">
                <div className="icon-container">
                  {feature.icon}
                  <div className="icon-glow"></div>
                </div>
                <div className="card-badge">{feature.highlight}</div>
              </div>

              <div className="card-content">
                <h3 className="card-title">{feature.title}</h3>
                <p className="card-description">{feature.description}</p>

                <div className="card-stats">
                  <Lock className="stats-icon" />
                  <span>{feature.stats}</span>
                </div>
              </div>

              <div className="card-footer">
                <button className="learn-more-btn">
                  <span>Learn More</span>
                  <ArrowRight className="arrow-icon" />
                </button>
              </div>

              {/* Card Glow Effect */}
              <div className="card-glow"></div>
            </motion.div>
          ))}
        </motion.div>
</section>

        {/* Image Sections */}
        {/* <div className="features-showcase">
          <ImageSections />
        </div> */}
      </div>
        <div className="features-showcase">
          <SectionI />
        </div>
    </section>
  )
}
