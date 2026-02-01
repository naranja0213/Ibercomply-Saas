import { redirect } from "next/navigation";

export default function AssessmentPage() {
  // 直接重定向，无 UI，这是技术路由
  redirect("/assessment/start");
}
