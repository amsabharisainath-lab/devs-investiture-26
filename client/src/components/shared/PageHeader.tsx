import BrandLogo from "./BrandLogo";

export default function PageHeader() {
  return (
    <header className="page-header">
      {/* Reusable Brand Logo component in static solid state */}
      <BrandLogo size="sm" />
      <div className="header-subtext">INVESTITURE</div>
    </header>
  );
}
