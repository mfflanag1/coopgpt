const out=[];for(let s=2;s<=24;s++){const last=2*s;let q=1/3;const values=[];
      for(let m=1;m<=last;m++){
        if(m>1){const k=Math.min(s-1,2*m-2);q*=k/(k+1);}
        values.push(1+2*(m-1)*q);
      }
      out.push({s,values});}process.stdout.write(JSON.stringify(out));
