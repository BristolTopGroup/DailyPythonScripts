from ROOT import *
import sys


xlimits = [0, 100]
xTitle = 'test X'
yTitle = 'test Y'

c = TCanvas("cname", 'cname', 1080, 1080)
pad1 = TPad("pad1", "The pad with the function",0.0,0.2,1.0,1.0);
pad2 = TPad("pad2","The pad with the histogram",0.0,0.0,1.0,0.2);
pad1.Draw()
pad2.Draw()
            
pad1.cd()
    
hFrame = (pad1.cd()).DrawFrame(xlimits[0],-.1,xlimits[1],1.1)
hFrame.GetXaxis().SetTitle(xTitle)
hFrame.GetYaxis().SetTitle(yTitle)
hFrame.Draw()
upper = TLine(xlimits[0],1.,xlimits[1],1.)
lower = TLine(xlimits[0],0.,xlimits[1],0.)
cut = TLine(30., 0., 30., 1.)
cut.SetLineColor(1)
upper.SetLineColor(4)
lower.SetLineColor(4)
upper.DrawLine(xlimits[0],1.,xlimits[1],1.) ;
lower.DrawLine(xlimits[0],0.,xlimits[1],0.) ;
cut.DrawLine(30., 0., 30., 1.)
            
tex = TLatex(0.18,1,"Just Testing");
tex.SetNDC();
tex.SetTextAlign(13);
tex.SetTextFont(42);
tex.SetTextSize(0.04);
tex.SetLineWidth(2);
tex.Draw();
            
pad2.cd()
hFrame = (pad2.cd()).DrawFrame(xlimits[0],0.,xlimits[1],2)
hFrame.GetXaxis().SetTitle(xTitle)
hFrame.GetYaxis().SetTitle(yTitle)
hFrame.Draw()
upper = TLine(xlimits[0],1.,xlimits[1],1.)
cut = TLine(30., -2., 30., 2.)
cut.SetLineColor(1)
upper.SetLineColor(4)
upper.DrawLine(xlimits[0],1.,xlimits[1],1.) ;
cut.DrawLine(30., -2., 30., 2.)


c.SaveAs("testSplit.pdf")
c.SaveAs("testSplit.png")