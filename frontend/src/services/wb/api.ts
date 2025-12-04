import BaseApi from "@/services/base-api";

export default class WbOrdersApi extends BaseApi {
  public async getAbcAnalytics(dates: any): Promise<any> {
    return await this.post(
      `/wb/orders`,
      dates,
    );
  }
}
