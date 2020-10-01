import six


class OfxPrinter():
    ofx = None
    out_filename = None
    out_handle = None
    term = "\r\n"

    def __init__(self, ofx, filename, term="\r\n"):
        self.ofx = ofx
        self.out_filename = filename
        self.term = term

    def writeLine(self, data, tabs=0, term=None):
        if term is None:
            term = self.term

        tabbing = (tabs * "\t") if (tabs > 0) else ''

        return self.out_handle.write(
            "{0}{1}{2}".format(
                tabbing,
                data,
                term
            )
        )

    def writeHeaders(self):
        for k, v in six.iteritems(self.ofx.headers):
            if v is None:
                self.writeLine("{0}:NONE".format(k))
            else:
                self.writeLine("{0}:{1}".format(k, v))
        self.writeLine("")

    def writeSignOn(self, tabs=0):
        # signon already has newlines and tabs in it
        # TODO: reimplement signon printing with tabs
        self.writeLine(self.ofx.signon.__str__(), term="")

    def printDate(self, dt, msec_digs=3):
        strdt = dt.strftime('%Y%m%d%H%M%S')
        strdt_msec = dt.strftime('%f')
        if len(strdt_msec) < msec_digs:
            strdt_msec += ('0' * (msec_digs - len(strdt_msec)))
        elif len(strdt_msec) > msec_digs:
            strdt_msec = strdt_msec[:msec_digs]
        return strdt + '.' + strdt_msec

    def writeInvestTrn(self, trn, tabs=0):
        self.writeLine("<{}>".format(trn.type.upper()), tabs=tabs)

        self.writeLine("<INVTRAN>", tabs=tabs)
        self.writeLine("<FITID>{}".format(trn.id), tabs=tabs)
        self.writeLine("<DTSETTLE>{}".format(self.printDate(trn.settleDate)), tabs=tabs)
        self.writeLine("<DTTRADE>{}".format(self.printDate(trn.tradeDate)), tabs=tabs)
        if len(trn.memo.strip()) > 0:
            self.writeLine("<MEMO>{}".format(trn.memo), tabs=tabs)
        self.writeLine("</INVTRAN>", tabs=tabs)

        self.writeLine("<INCOMETYPE>{}".format(trn.income_type), tabs=tabs)
        self.writeLine("<UNITS>{}".format(float(trn.units)), tabs=tabs)
        self.writeLine("<UNITPRICE>{}".format(float(trn.unit_price)), tabs=tabs)
        self.writeLine("<COMMISSION>{}".format(float(trn.commission)), tabs=tabs)
        self.writeLine("<FEES>{}".format(float(trn.fees)), tabs=tabs)
        self.writeLine("<TOTAL>{}".format(float(trn.total)), tabs=tabs)
        self.writeLine("<TFERACTION>{}".format(trn.tferaction), tabs=tabs)
        self.writeLine("</{}>".format(trn.type.upper()), tabs=tabs)

    def writeInvestPos(self, trn, tabs=0):
        self.writeLine("<POSMF>", tabs=tabs)
        self.writeLine("<INVPOS>", tabs=tabs)
        self.writeLine("<SECID>", tabs=tabs)
        self.writeLine("<UNIQUEID>{}".format(trn.security), tabs=tabs)
        self.writeLine("<UNIQUEIDTYPE>CUSIP", tabs=tabs)
        self.writeLine("</SECID>", tabs=tabs)

        self.writeLine("<DTPRICEASOF>{}".format(self.printDate(trn.date)), tabs=tabs)
        self.writeLine("<UNITS>{}".format(float(trn.units)), tabs=tabs)
        self.writeLine("<UNITPRICE>{}".format(float(trn.unit_price)), tabs=tabs)
        self.writeLine("<MKTVALMKTVAL>{}".format(float(trn.market_value)), tabs=tabs)
        self.writeLine("</POSMF>", tabs=tabs)
        self.writeLine("</INVPOS>", tabs=tabs)

        # tabs -= 1

    def writeTrn(self, trn, tabs=5):
        self.writeLine("<STMTTRN>", tabs=tabs)
        # tabs += 1

        self.writeLine("<TRNTYPE>{}".format(trn.type.upper()), tabs=tabs)

        self.writeLine("<DTPOSTED>{}".format(
            self.printDate(trn.date)
        ), tabs=tabs)
        self.writeLine("<TRNAMT>{0:.2f}".format(float(trn.amount)), tabs=tabs)

        self.writeLine("<FITID>{}".format(trn.id), tabs=tabs)

        if len(str(trn.checknum)) > 0:
            self.writeLine("<CHECKNUM>{}".format(
                trn.checknum
            ), tabs=tabs)

        self.writeLine("<NAME>{}".format(trn.payee), tabs=tabs)

        if len(trn.memo.strip()) > 0:
            self.writeLine("<MEMO>{}".format(trn.memo), tabs=tabs)

        # tabs -= 1
        self.writeLine("</STMTTRN>", tabs=tabs)

    def writeLedgerBal(self, statement, tabs=4):
        bal = getattr(statement, 'balance', None)
        baldt = getattr(statement, 'balance_date', None)

        if bal and baldt:
            self.writeLine("<LEDGERBAL>", tabs=tabs)
            self.writeLine("<BALAMT>{0:.2f}".format(float(bal)), tabs=tabs+1)
            self.writeLine("<DTASOF>{0}".format(
                self.printDate(baldt)
            ), tabs=tabs)
            self.writeLine("</LEDGERBAL>", tabs=tabs)

    def writeAvailBal(self, statement, tabs=4):
        bal = getattr(statement, 'available_balance', None)
        baldt = getattr(statement, 'available_balance_date', None)

        if bal and baldt:
            self.writeLine("<AVAILBAL>", tabs=tabs)
            self.writeLine("<BALAMT>{0:.2f}".format(float(bal)), tabs=tabs+1)
            self.writeLine("<DTASOF>{0}".format(
                self.printDate(baldt)
            ), tabs=tabs)
            self.writeLine("</AVAILBAL>", tabs=tabs)

    def writeBnkAcctStmTrs(self,tabs,acct):
        self.writeLine("<STMTRS>", tabs=tabs)
        # tabs += 1

        if acct.curdef:
            self.writeLine("<CURDEF>{0}".format(
                acct.curdef
            ), tabs=tabs)

        if acct.routing_number or acct.account_id or acct.account_type:
            self.writeLine("<BANKACCTFROM>", tabs=tabs)
            if acct.routing_number:
                self.writeLine("<BANKID>{0}".format(
                    acct.routing_number
                ), tabs=tabs)
            if acct.account_id:
                self.writeLine("<ACCTID>{0}".format(
                    acct.account_id
                ), tabs=tabs)
            if acct.account_type:
                self.writeLine("<ACCTTYPE>{0}".format(
                    acct.account_type
                ), tabs=tabs)
            self.writeLine("</BANKACCTFROM>", tabs=tabs)

        self.writeLine("<BANKTRANLIST>", tabs=tabs)
        # tabs += 1
        self.writeLine("<DTSTART>{0}".format(
            self.printDate(acct.statement.start_date)
        ), tabs=tabs)
        self.writeLine("<DTEND>{0}".format(
            self.printDate(acct.statement.end_date)
        ), tabs=tabs)

        for trn in acct.statement.transactions:
            self.writeTrn(trn, tabs=tabs)

        # tabs -= 1

        self.writeLine("</BANKTRANLIST>", tabs=tabs)

        self.writeLedgerBal(acct.statement, tabs=tabs)
        self.writeAvailBal(acct.statement, tabs=tabs)

        # tabs -= 1

        self.writeLine("</STMTRS>", tabs=tabs)

    def writeInvestAcctStmTrs(self,tabs,acct):
        tabs = 0
        self.writeLine("<INVSTMTRS>", tabs=tabs)
        # tabs += 1

        if acct.account_id:
            self.writeLine("<ACCTID>{0}".format(
                acct.account_id
            ), tabs=tabs)
        if acct.account_type:
            self.writeLine("<ACCTTYPE>{0}".format(
                acct.account_type
            ), tabs=tabs)

        if acct.curdef:
            self.writeLine("<CURDEF>{0}".format(
                acct.curdef
            ), tabs=tabs)

        self.writeLine("<INVTRANLIST>", tabs=tabs)
        self.writeLine("<DTSTART>{0}".format(
            self.printDate(acct.statement.start_date)
        ), tabs=tabs)
        self.writeLine("<DTEND>{0}".format(
            self.printDate(acct.statement.end_date)
        ), tabs=tabs)
        tabs = 0
        for trn in acct.statement.transactions:
            self.writeInvestTrn(trn, tabs=tabs)
        self.writeLine("</INVTRANLIST>", tabs=tabs)

        # WHAT ABOUT POSITIONS?
        self.writeLine("<INVPOSLIST>", tabs=tabs)
        for trn in acct.statement.positions:
            self.writeInvestPos(trn, tabs=tabs)
        self.writeLine("</INVPOSLIST>", tabs=tabs)

        self.writeLedgerBal(acct.statement, tabs=tabs)
        self.writeAvailBal(acct.statement, tabs=tabs)

        # tabs -= 1

        self.writeLine("</INVSTMTRS>", tabs=tabs)

    def writeStmTrs(self, tabs=0):
        for acct in self.ofx.accounts:
            if acct.type == 1:
                self.writeBnkAcctStmTrs(tabs,acct)
            if acct.type == 3:
                if not len(acct.statement.transactions): continue
                self.writeInvestAcctStmTrs(tabs,acct)
                # todo
                break

    def writeBankMsgsRsv1(self, tabs=0):
        if self.ofx.account.type == 1:
            self.writeLine("<BANKMSGSRSV1>", tabs=tabs)
            # tabs += 1
            self.writeLine("<STMTTRNRS>", tabs=tabs)
        elif self.ofx.account.type == 3:
            self.writeLine("<INVSTMTMSGSRSV1>", tabs=tabs)
        # tabs += 1
            self.writeLine("<INVSTMTTRNRS>", tabs=tabs)
        # tabs += 1
        if self.ofx.trnuid is not None:
            self.writeLine("<TRNUID>{0}".format(
                self.ofx.trnuid
            ), tabs=tabs)
        if self.ofx.status:
            self.writeLine("<STATUS>", tabs=tabs)
            self.writeLine("<CODE>{0}".format(
                self.ofx.status['code']
            ), tabs=tabs)
            self.writeLine("<SEVERITY>{0}".format(
                self.ofx.status['severity']
            ), tabs=tabs)
            self.writeLine("</STATUS>", tabs=tabs)
        self.writeStmTrs(tabs=tabs)
        if self.ofx.account.type == 1:
            # tabs -= 1
            self.writeLine("</STMTTRNRS>", tabs=tabs)
            # tabs -= 1
            self.writeLine("</BANKMSGSRSV1>", tabs=tabs)
        elif self.ofx.account.type == 3:
            # tabs -= 1
            self.writeLine("</INVSTMTMSGSRSV1>", tabs=tabs)
            # tabs -= 1
            self.writeLine("</INVSTMTTRNRS>", tabs=tabs)

    def writeOfx(self, tabs=0):
        self.writeLine("<OFX>", tabs=tabs)
        # tabs += 1
        self.writeSignOn(tabs=tabs)
        self.writeBankMsgsRsv1(tabs=tabs)
        # tabs -= 1
        # No newline at end of file
        self.writeLine("</OFX>", tabs=tabs, term="")

    def writeToFile(self, fileObject, tabs=0):
        if self.out_handle:
            raise Exception("Already writing file")

        self.out_handle = fileObject

        self.writeHeaders()

        self.writeOfx(tabs=tabs)

        self.out_handle.flush()
        self.out_handle = None

    def write(self, filename=None, tabs=0):
        if filename is None:
            filename = self.out_filename

        with open(filename, 'w') as f:
            self.writeToFile(f)
